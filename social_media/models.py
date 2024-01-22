import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def profile_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    full_name = instance.owner.first_name + " " + instance.owner.last_name
    filename = f"{slugify(full_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profiles/", filename)


class Profile(models.Model):
    class GenderChoices(models.Choices):
        MALE = "Male"
        FEMALE = "Female"

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    gender = models.CharField(max_length=15, choices=GenderChoices.choices)
    bio = models.TextField(max_length=255, null=True,blank=True)
    phone_number = models.CharField(max_length=18, null=True, blank=True)
    image = models.ImageField(null=True, upload_to=profile_image_file_path)

    def __str__(self):
        return str(self.owner.first_name + " " + self.owner.last_name)
