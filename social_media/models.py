import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def profile_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.owner.full_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "profiles", filename)


class Profile(models.Model):
    class GenderChoices(models.Choices):
        MALE = "Male"
        FEMALE = "Female"

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    gender = models.CharField(max_length=15, choices=GenderChoices.choices)
    bio = models.TextField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=18, null=True, blank=True)
    image = models.ImageField(null=True, upload_to=profile_image_file_path)
    following = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="followers"
    )

    def __str__(self):
        return str(self.owner.full_name)


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = (
        f"id_owner_{slugify(instance.owner.id)}"
        f"_{slugify(instance.owner.full_name)}"
        f"-{uuid.uuid4()}{extension}"
    )

    return os.path.join("uploads", "posts", filename)


class Post(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    text = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    hashtag = models.CharField(max_length=125, null=True, blank=True)
    image = models.ImageField(
        null=True, upload_to=post_image_file_path, blank=True
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.full_name} added comments to {self.post.id}"


class Like(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes"
    )
