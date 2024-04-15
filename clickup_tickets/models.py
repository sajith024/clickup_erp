from django.db.models import Model
from django.db.models import (
    CharField,
    TextField,
    DateField,
    DateTimeField,
    DurationField,
    IntegerField,
    FileField,
)
from django.db.models import ForeignKey, CASCADE, SET_NULL, ManyToManyField
from django.core.validators import RegexValidator
from django.utils.timezone import timedelta

from clickup_utils.utils import (
    generate_uuid,
    ticket_attachment_path,
    ticket_allocation_attachment_path,
)
from clickup_projects.models import Employee, TeamMember, Lists, Sprints


# Create your models here.
class Priority(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    title = CharField()

    def __str__(self) -> str:
        return self.title


class TicketStatus(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    title = CharField()
    icon = CharField()
    colorInfo = CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Enter a valid color code. Example: #RRGGBB or #RGB",
                code="invalid_color",
            )
        ],
    )

    def __str__(self) -> str:
        return self.title


class Ticket(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    type = CharField()
    title = CharField()
    customId = CharField(unique=True, editable=False)
    description = TextField()
    startDate = DateField(null=True, blank=True)
    dueDate = DateField(null=True, blank=True)
    priority = ForeignKey(Priority, on_delete=SET_NULL, null=True)
    list = ForeignKey(
        Lists, on_delete=CASCADE, related_name="ticket_list", null=True, blank=True
    )
    sprint = ForeignKey(
        Sprints, on_delete=CASCADE, related_name="ticket_sprint", null=True, blank=True
    )
    createdAt = DateTimeField(auto_now=True)
    updatedAt = DateTimeField(auto_now_add=True)
    createdBy = ManyToManyField(Employee, related_name="created_ticket")
    updatedBy = ManyToManyField(
        Employee,
        related_name="updated_ticket",
        blank=True,
    )
    deletedBy = ManyToManyField(
        Employee,
        related_name="deleted_ticket",
        blank=True,
    )

    def generate_custom_id(self):
        if self.list:
            short_code = self.list.project.shortCode
        else:
            short_code = self.sprint.project.shortCode

        last_instance = Ticket.objects.order_by("customId").last()

        if last_instance:
            last_id = int(last_instance.customId[3:])
            new_id = last_id + 1
        else:
            new_id = 1
        return f"{short_code}{new_id:05d}"

    def save(self, *args, **kwargs):
        if not self.customId:
            self.customId = self.generate_custom_id()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class TicketAllocation(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )
    title = CharField()
    priority = ForeignKey(Priority, on_delete=SET_NULL, null=True)
    ticketStatus = ForeignKey(TicketStatus, on_delete=SET_NULL, null=True)
    customId = CharField(unique=True, editable=False)
    estimationHours = DurationField(default=timedelta(hours=1))
    description = TextField()
    startDate = DateField(null=True, blank=True)
    dueDate = DateField(null=True, blank=True)
    assignedUsers = ManyToManyField(TeamMember, blank=True)
    ticket = ForeignKey(Ticket, on_delete=CASCADE, related_name="allocations")
    createdAt = DateTimeField(auto_now=True)
    updatedAt = DateTimeField(auto_now_add=True)
    createdBy = ManyToManyField(
        Employee,
        related_name="created_allocations",
    )
    updatedBy = ManyToManyField(
        Employee,
        related_name="updated_allocations",
        blank=True,
    )
    deletedBy = ManyToManyField(
        Employee,
        related_name="deleted_allocations",
        blank=True,
    )
    _v = IntegerField(default=0)

    def generate_custom_id(self):
        custom_id = self.ticket.customId
        last_instance = self.ticket.allocations.last()
        if last_instance:
            last_id = int(last_instance.customId.split("#")[1])
            new_id = last_id + 1
        else:
            new_id = 1
        return f"{custom_id}#{new_id}"

    def save(self, *args, **kwargs):
        if not self.customId:
            self.customId = self.generate_custom_id()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class TicketAttachment(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )

    type = CharField()
    ticket = ForeignKey(Ticket, on_delete=CASCADE, related_name="attachment")
    files = FileField(upload_to=ticket_attachment_path)

    def __str__(self) -> str:
        return self.file.path


class TicketAllocationAttachment(Model):
    _id = CharField(
        primary_key=True, default=generate_uuid, max_length=32, editable=False
    )

    type = CharField()
    ticket_allocation = ForeignKey(
        TicketAllocation, on_delete=CASCADE, related_name="attachment"
    )
    files = FileField(upload_to=ticket_allocation_attachment_path)

    def __str__(self) -> str:
        return self.file.path
