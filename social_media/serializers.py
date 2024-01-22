from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from social_media.models import Profile
from user.serializers import UserUpdateForProfileSerializer


class ProfileSerializer(serializers.ModelSerializer):
    owner = UserUpdateForProfileSerializer(many=False, partial=True)

    def validate(self, attrs):
        data = super(ProfileSerializer, self).validate(attrs=attrs)

        user = self.context["request"].user
        existing_profile = Profile.objects.filter(owner=user).first()

        if existing_profile and self.instance != existing_profile:
            raise ValidationError({"error": "You already have a profile."})

        return data

    class Meta:
        model = Profile
        fields = ("id", "owner", "gender", "bio", "phone_number", "image")
        read_only_fields = ("id", "image")

    def update(self, instance, validated_data):

        owner_data = validated_data.pop("owner", {})
        fields_to_update = ["gender", "bio", "phone_number"]

        for field in fields_to_update:
            value = validated_data.get(field, getattr(instance, field))
            setattr(instance, field, value)

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
        fields = ("id", "first_name", "last_name", "gender", "bio", "phone_number", "image")


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "image")
