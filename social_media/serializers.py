from rest_framework import serializers

from social_media.models import Profile
from user.serializers import UserUpdateForProfileSerializer


class ProfileSerializer(serializers.ModelSerializer):
    owner = UserUpdateForProfileSerializer(many=False, partial=True)

    class Meta:
        model = Profile
        fields = ("id", "owner", "gender", "bio", "phone_number")

    def update(self, instance, validated_data):
        owner_data = validated_data.pop("owner", {})
        instance.gender = validated_data.get("gender", instance.gender)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)
        instance.save()

        # Оновлюємо дані власника
        owner = instance.owner
        owner.first_name = owner_data.get("first_name", owner.first_name)
        owner.last_name = owner_data.get("last_name", owner.last_name)
        owner.save()

        return instance


class ProfileListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="owner.first_name")
    last_name = serializers.CharField(source="owner.last_name")

    class Meta:
        model = Profile
        fields = ("id", "first_name", "last_name", "gender", "bio", "phone_number")
