from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from social_media.models import Profile, Post
from social_media.permissions import IsOwnerOrIfAuthenticatedReadOnly
from social_media.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    ProfileImageSerializer,
    PostSerializer,
    PostListSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrIfAuthenticatedReadOnly,)

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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            {"detail": "You are now following this user."}, status=status.HTTP_200_OK
        )

    @action(methods=["GET"], detail=True)
    def unfolow(self, request, pk=None):
        profile_to_unfollow = self.get_object()

        if not self.request.user.profile.following.filter(
            id=profile_to_unfollow.id
        ).exists():
            return Response(
                {"detail": "You are not unfollow this user."}, status=status.HTTP_200_OK
            )

        self.request.user.profile.following.remove(profile_to_unfollow)
        return Response(
            {"detail": "You have unfollowed this user"}, status=status.HTTP_200_OK
        )

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
