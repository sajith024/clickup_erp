from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext as _

from . import models


class ClickUpUserManager(BaseUserManager):

    def create_user(
        self, username, password=None, email=None, role=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)        
        if not username:
            raise ValueError("The given username must be set")
        if not role:
            raise ValueError("The given role must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        role = models.Role.objects.get_or_create(name="Admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(username, password, role=role[0], **extra_fields)
