from rest_framework import serializers

from social_media.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "gender", "bio", "phone_number")


class ProfileListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="owner.first_name")
    last_name = serializers.CharField(source="owner.last_name")

    class Meta:
        model = Profile
        fields = ("id", "first_name", "last_name", "gender", "bio", "phone_number")
