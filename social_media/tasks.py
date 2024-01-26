import base64
import io
import os

import PIL.Image as Image
from django.core.files import File

from app import settings
from social_media.models import Post

from celery import shared_task


def correct_data_for_post(owner_id: int, post_data: dict) -> dict:
    data = {
        key: value
        for key, value in post_data.items()
        if key not in ["csrfmiddlewaretoken", "scheduled_time", "image"]
    }
    data["owner_id"] = owner_id
    return data


def process_image_data(data_image: dict) -> None:
    byte_data = data_image["image"].encode(encoding="utf-8")
    base = base64.b64decode(byte_data)
    img = Image.open(io.BytesIO(base))
    image_path = os.path.join(settings.MEDIA_ROOT, data_image["name"])
    img.save(image_path, format=img.format)


@shared_task
def create_scheduled_post(
    owner_id: int, post_data: dict, data_image=None
) -> None:
    data = correct_data_for_post(owner_id, post_data)

    if data_image:
        process_image_data(data_image)
        image_path = os.path.join(settings.MEDIA_ROOT, data_image["name"])

        with open(image_path, "rb") as file:
            picture = File(file)

            Post.objects.create(**data, image=picture)

        os.remove(image_path)
    else:
        Post.objects.create(**data)
