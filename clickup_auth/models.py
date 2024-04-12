from django.contrib.auth.models import AbstractUser
from django.db.models import CharField

from clickup_utils.utils import generate_uuid
from .managers import ClickUpUserManager


# Create your models here.
class ClickUpUser(AbstractUser):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )

    objects = ClickUpUserManager()