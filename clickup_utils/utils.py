from uuid import uuid4

from django.utils.timezone import now


def generate_uuid():
    return uuid4().hex


def image_upload_path(instance, filename):
    time_now = now()
    return f"project/logo/{time_now.year}/{time_now.month}/{filename}"


def ticket_attachment_path(instance, filename):
    return f"attachment/ticket/{instance.ticket._id}/{filename}"


def ticket_allocation_attachment_path(instance, filename):
    return f"attachment/ticket_allocation/{instance.ticket_allocation._id}/{filename}"
