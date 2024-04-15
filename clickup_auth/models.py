from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField

from clickup_utils.utils import generate_uuid
from .managers import ClickUpUserManager


# Create your models here.
class ClickUpUser(AbstractUser):
    id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )

    email = EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)

    objects = ClickUpUserManager()
