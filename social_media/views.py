from django.shortcuts import render
from rest_framework import viewsets

from social_media.models import Profile
from social_media.serializers import ProfileSerializer, ProfileListSerializer


# Create your views here.
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        return ProfileSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
