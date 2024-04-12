from uuid import uuid4

from django.utils.timezone import now


def generate_uuid():
    return uuid4().hex


def image_upload_path(instance, filename):
    time_now = now()
    return f"project/logo/{time_now.year}/{time_now.month}/{filename}"
