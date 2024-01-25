from social_media.models import Post

from celery import shared_task


def correct_data_for_post(owmer_id, post_data):
    data = {
        key: value
        for key, value in post_data.items()
        if key not in ["csrfmiddlewaretoken", "scheduled_time"]
    }
    data["owner_id"] = owmer_id
    return data


@shared_task
def create_scheduled_post(owner_id, post_data):
    data = correct_data_for_post(owner_id, post_data)
    Post.objects.create(**data)
