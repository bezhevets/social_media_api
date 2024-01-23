from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from social_media.models import Profile, Post, Comment, Like
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
        fields = ("id", "owner", "gender", "bio", "phone_number", "following", "image")
        read_only_fields = ("id", "following", "image")

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
    count_following = serializers.IntegerField(source="following.count")
    count_followers = serializers.IntegerField(source="followers.count")

    class Meta:
        model = Profile
        fields = (
            "id",
            "first_name",
            "last_name",
            "gender",
            "bio",
            "phone_number",
            "count_followers",
            "count_following",
            "image",
        )


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "image")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "text", "created_at")


class CommentCreateSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = ("id", "post", "text", "created_at")


class CommentDetailSerializer(CommentSerializer):
    owner = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="full_name"
    )

    class Meta:
        model = Comment
        fields = ("id", "owner", "text", "created_at")


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "post")


class LikeDetailSerializer(LikeSerializer):
    like = serializers.ReadOnlyField(source="owner.full_name")

    class Meta:
        model = Like
        fields = ("id", "post", "like")


class PostSerializer(serializers.ModelSerializer):
    comments = CommentDetailSerializer(many=True, read_only=True)
    likes = LikeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("id", "text", "created_at", "hashtag", "image", "comments", "likes")


class PostListSerializer(PostSerializer):
    owner = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="full_name"
    )
    comments_count = serializers.IntegerField()
    likes = serializers.IntegerField(source="likes.count")

    class Meta:
        model = Post
        fields = (
            "id",
            "owner",
            "text",
            "hashtag",
            "image",
            "comments_count",
            "likes",
            "created_at",
        )
