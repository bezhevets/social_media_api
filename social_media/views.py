import base64
import os
from datetime import datetime
import pytz

from django.db.models import Q, Count, Prefetch
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Profile, Post, Comment, Like
from social_media.permissions import IsOwnerOrIfAuthenticatedReadOnly
from social_media.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    ProfileImageSerializer,
    PostSerializer,
    PostListSerializer,
    PostUpdateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    LikeSerializer,
    LikeDetailSerializer,
)
from social_media.tasks import create_scheduled_post
from dotenv import load_dotenv

load_dotenv()


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = (
        Profile.objects.all()
        .select_related("owner")
        .prefetch_related("following", "followers")
    )
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrIfAuthenticatedReadOnly)

    def get_queryset(self):
        queryset = self.queryset

        last_name = self.request.query_params.get("last_name")
        first_name = self.request.query_params.get("first_name")
        if last_name:
            queryset = queryset.filter(owner__last_name__icontains=last_name)
        if first_name:
            queryset = queryset.filter(owner__first_name__icontains=first_name)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        if self.action == "upload_image":
            return ProfileImageSerializer
        return ProfileSerializer

    def perform_create(self, serializer):
        owner = self.request.user
        owner.first_name = self.request.data.get("owner.first_name")
        owner.last_name = self.request.data.get("owner.last_name")
        owner.save()

        serializer.save(owner=owner)

    @action(
        methods=["GET", "POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=True)
    def follow(self, request, pk=None):
        profile_to_follow = self.get_object()

        if self.request.user.profile == profile_to_follow:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if profile_to_follow in self.request.user.profile.following.all():
            return Response(
                {"detail": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.request.user.profile.following.add(profile_to_follow)
        return Response(
            {"detail": "You are now following this user."},
            status=status.HTTP_200_OK,
        )

    @action(methods=["GET"], detail=True)
    def unfollow(self, request, pk=None):
        profile_to_unfollow = self.get_object()

        if not self.request.user.profile.following.filter(
            id=profile_to_unfollow.id
        ).exists():
            return Response(
                {"detail": "You are not unfollow this user."},
                status=status.HTTP_200_OK,
            )

        self.request.user.profile.following.remove(profile_to_unfollow)
        return Response(
            {"detail": "You have unfollowed this user"},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "last_name",
                type=str,
                description="Filter by last_name",
                required=False,
            ),
            OpenApiParameter(
                "first_name",
                type=str,
                description="Filter by first_name",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.all().select_related("owner").prefetch_related("likes")
    )
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrIfAuthenticatedReadOnly)

    @staticmethod
    def image_decoding(file):
        image = file.read()
        byte = base64.b64encode(image)
        data_image = {"image": byte.decode("utf-8"), "name": file.name}
        return data_image

    def get_queryset(self):
        queryset = self.queryset

        author_id_str = self.request.query_params.get("author")
        hashtag = self.request.query_params.get("hashtag")
        if author_id_str or hashtag:
            if author_id_str:
                queryset = queryset.filter(owner_id=int(author_id_str))

            if hashtag:
                queryset = queryset.filter(hashtag__icontains=hashtag)
            return queryset.distinct()

        if self.action == "list":
            queryset = self.queryset.filter(
                Q(owner__profile__followers=self.request.user.profile)
                | Q(owner__profile=self.request.user.profile)
            ).order_by("-created_at")
        queryset = queryset.annotate(comments_count=Count("comments"))

        queryset = queryset.prefetch_related(
            Prefetch(
                "comments",
                queryset=Comment.objects.all().select_related("owner"),
            )
        )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "update":
            return PostUpdateSerializer
        if self.action == "create_comment":
            return CommentSerializer
        return PostSerializer

    def create(self, request, *args, **kwargs):
        scheduled_time_str = request.data.get("scheduled_time")
        if scheduled_time_str:
            scheduled_time_datetime = datetime.strptime(
                scheduled_time_str, "%Y-%m-%dT%H:%M"
            )
            if datetime.now() >= scheduled_time_datetime:
                request_data_copy = request.data.copy()
                request_data_copy.pop("scheduled_time")
                serializer = self.get_serializer(data=request_data_copy)
                serializer.is_valid(raise_exception=True)
                serializer.save(owner=self.request.user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                data_image = None
                request = request.data.copy()

                if request.get("image"):
                    data_image = self.image_decoding(
                        self.request.FILES["image"]
                    )
                    request.pop("image")

                tz = pytz.timezone(os.environ["TZ"])
                create_scheduled_post.apply_async(
                    args=[self.request.user.id, request, data_image],
                    eta=tz.localize(scheduled_time_datetime),
                )
                return Response(
                    {"status": "Post will be created at scheduled time."},
                    status=status.HTTP_202_ACCEPTED,
                )
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=self.request.user)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

    @action(
        detail=True,
        methods=["POST"],
        url_path="create_comment",
        permission_classes=[IsAuthenticated],
    )
    def create_comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "author",
                type=str,
                description="Filter by author",
                required=False,
            ),
            OpenApiParameter(
                "hashtag",
                type=str,
                description="Filter by hashtag",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrIfAuthenticatedReadOnly)

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "destroy"]:
            return CommentSerializer
        return CommentCreateSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all().select_related("owner", "post")
    permission_classes = (IsAuthenticated, IsOwnerOrIfAuthenticatedReadOnly)

    def get_serializer_class(self):
        if self.action == "list":
            return LikeDetailSerializer
        return LikeSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.request.data["post"])
        user = self.request.user

        likes = Like.objects.filter(owner=user, post=post)
        if likes:
            likes.delete()
        else:
            serializer.save(owner=user, post=post)
