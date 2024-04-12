from django.db.models import Model
from django.db.models import (
    TextField,
    CharField,
    IntegerField,
    ImageField,
    BooleanField,
    DateTimeField,
    DurationField,
)
from django.core.validators import RegexValidator
from django.db.models import ForeignKey, ManyToManyField, OneToOneField, CASCADE
from django.utils.timezone import timedelta

from clickup_utils.utils import generate_uuid, image_upload_path
from clickup_auth.models import ClickUpUser


# Create your models here.
class Jokes(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    joke = TextField()

    def __str__(self) -> str:
        return self.joke


class Project(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    name = CharField()
    erpId = IntegerField()
    shortCode = CharField(max_length=3)
    logo = ImageField(upload_to=image_upload_path, default="", blank=True)

    def __str__(self) -> str:
        return self.name


class Lists(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    name = CharField()
    project = ForeignKey(Project, on_delete=CASCADE, related_name="lists")

    def __str__(self) -> str:
        return self.name


class Folders(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    name = CharField()
    project = ForeignKey(Project, on_delete=CASCADE, related_name="folders")
    list = ManyToManyField(Lists, blank=True, related_name="folders")

    def __str__(self) -> str:
        return self.name


class Sprints(Model):
    SPRINT_STATUS = {
        "isActive": "IsActive",
        "Completed": "Completed",
    }
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    name = CharField()
    active = BooleanField()
    status = CharField(choices=SPRINT_STATUS, default="isActive")
    project = ForeignKey(Project, on_delete=CASCADE, related_name="sprint")

    def __str__(self) -> str:
        return self.name


class ProjectIcons(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    colorCode = CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Enter a valid color code. Example: #RRGGBB or #RGB",
                code="invalid_color",
            )
        ],
    )
    type = CharField()
    updatedAt = DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.colorCode


class Department(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    name = CharField()

    def __str__(self) -> str:
        return self.name


class Role(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    name = CharField()
    department = ForeignKey(Department, on_delete=CASCADE)

    def __str__(self) -> str:
        return self.name


class Skill(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    name = CharField()

    def __str__(self) -> str:
        return self.name


class Education(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    name = CharField()

    def __str__(self) -> str:
        return self.name


class Employee(Model):
    THEMES_MODE = {"light": "Light", "dark": "Dark"}

    DATE_FORMAT = {
        "dd-mm-yyyy": "dd-mm-yyyy",
    }

    TIME_FORMAT = {
        "24hr": "24hr",
    }

    TOAST_POSITION = {
        "OFF": "OFF",
    }

    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    user = ForeignKey(ClickUpUser, on_delete=CASCADE)
    employeeId = CharField()
    photo = ImageField(null=True, blank=True)
    role = ForeignKey(Role, on_delete=CASCADE)
    skillSet = ManyToManyField(Skill, blank=True)
    theme = CharField(choices=THEMES_MODE, default="light")
    dateFormat = CharField(choices=DATE_FORMAT, default="dd-mm-yyyy")
    timeFormat = CharField(choices=TIME_FORMAT, default="24hr")
    toastPosition = CharField(choices=TOAST_POSITION, default="OFF")
    contactNumber = CharField()
    education = ManyToManyField(Education, blank=True)

    def __str__(self) -> str:
        return self.user.get_short_name()


class TeamMember(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    user = OneToOneField(Employee, on_delete=CASCADE)
    allocationHours = DurationField(default=timedelta(hours=1))
    lastWorked = DateTimeField(null=True, blank=True)
    performanceIndex = IntegerField(default=0)
    qualityIndex = IntegerField(default=0)
    project = ManyToManyField(Project)

    def __str__(self) -> str:
        return self.user.user.get_short_name()
