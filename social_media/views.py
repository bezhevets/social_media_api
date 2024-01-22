from rest_framework import viewsets

from social_media.models import Profile
from social_media.permissions import IsOwnerOrIfAuthenticatedReadOnly
from social_media.serializers import ProfileSerializer, ProfileListSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        return ProfileSerializer

    def perform_create(self, serializer):
        owner = self.request.user
        owner.first_name = self.request.data.get("owner.first_name")
        owner.last_name = self.request.data.get("owner.last_name")
        owner.save()

        serializer.save(owner=owner)
