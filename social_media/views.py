from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from social_media.models import Profile
from social_media.permissions import IsOwnerOrIfAuthenticatedReadOnly
from social_media.serializers import ProfileSerializer, ProfileListSerializer, ProfileImageSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrIfAuthenticatedReadOnly,)

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

    @action(
        methods=["GET"],
        detail=True
    )
    def follow(self, request, pk=None):
        profile_to_follow = self.get_object()

        if self.request.user.profile == profile_to_follow:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if profile_to_follow in self.request.user.profile.following.all():
            return Response(
                {"detail": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.request.user.profile.following.add(profile_to_follow)
        return Response(
                {"detail": "You are now following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
