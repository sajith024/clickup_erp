from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.serializers import CharField
from rest_framework.serializers import ValidationError

from .models import (
    Priority,
    TicketStatus,
    TicketAllocation,
    Ticket,
    TicketAllocationAttachment,
    TicketAttachment,
)

from clickup_projects.models import TeamMember, Employee
from clickup_projects.serializers import TeamMemberSerializer


class PrioritySerializer(ModelSerializer):
    class Meta:
        model = Priority
        fields = "__all__"


class TicketStatusSerializer(ModelSerializer):
    class Meta:
        model = TicketStatus
        fields = "__all__"


class TicketEmployeeSerializer(ModelSerializer):
    employeeName = CharField(source="user.get_full_name")

    class Meta:
        model = Employee
        fields = ("_id", "employeeName", "photo")


class TicketAllocationSerializer(ModelSerializer):
    assignedUsers = TeamMemberSerializer(many=True)
    createdBy = TicketEmployeeSerializer()
    updatedBy = TicketEmployeeSerializer()
    deletedBy = TicketEmployeeSerializer()

    class Meta:
        model = TicketAllocation
        fields = "__all__"


class AllocationTeamMemberSerializer(ModelSerializer):
    user = CharField(source="_id")

    class Meta:
        model = TeamMember
        fields = ("user",)


class TicketAllocationUpdateSerializer(ModelSerializer):
    assignedUsers = AllocationTeamMemberSerializer(many=True)

    class Meta:
        model = TicketAllocation
        fields = (
            "title",
            "priority",
            "ticketStatus",
            "estimationHours",
            "description",
            "startDate",
            "dueDate",
            "assignedUsers",
        )

    def create(self, validated_data):
        assigned_users_data = validated_data.pop("assignedUsers")
        allocation = TicketAllocation.objects.create(**validated_data)

        for user in assigned_users_data:
            team_member = TeamMember.objects.get(**user)
            allocation.assignedUsers.add(team_member)
        return allocation

    def update(self, instance: TicketAllocation, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.priority = validated_data.get("priority", instance.priority)
        instance.ticketStatus = validated_data.get(
            "ticketStatus", instance.ticketStatus
        )
        instance.estimationHours = validated_data.get(
            "estimationHours", instance.estimationHours
        )
        instance.description = validated_data.get("description", instance.description)
        instance.startDate = validated_data.get("startDate", instance.startDate)
        instance.dueDate = validated_data.get("dueDate", instance.dueDate)

        if validated_data.get("assignedUsers"):
            assigned_users_data = validated_data.get("assignedUsers")

            for user in assigned_users_data:
                try:
                    TeamMember.objects.get(**user)
                except TeamMember.DoesNotExist:
                    raise ValidationError("User Doesn't Exist")

            instance.assignedUsers.clear()

            for user in assigned_users_data:
                team_member = TeamMember.objects.get(**user)
                instance.assignedUsers.add(team_member)

        return instance


class TicketSerializer(ModelSerializer):
    allocations = TicketAllocationSerializer(many=True)

    class Meta:
        model = Ticket
        fields = (
            "_id",
            "type",
            "title",
            "customId",
            "description",
            "startDate",
            "dueDate",
            "priority",
            "list",
            "sprint",
            "createdAt",
            "updatedAt",
            "allocations",
            "createdBy",
            "updatedBy",
            "deletedBy",
        )


class TicketGroupSerializer(Serializer):
    _id = CharField()
    groupById = CharField()
    data = TicketSerializer(many=True)


class TicketUpdateSerializer(ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "title",
            "description",
            "startDate",
            "dueDate",
            "priority",
        )


class TicketAllocationAttachmentUpdateSerializer(ModelSerializer):
    class Meta:
        model = TicketAllocationAttachment
        fields = ("files",)

    def create(self, validated_data):
        allocation_id = self.context["allocation_id"]
        try:
            TicketAllocation.objects.get(_id=allocation_id)
        except TicketAllocation.DoesNotExist:
            raise ValidationError("Ticket Allocation doesn't Exist")
        validated_data["ticket_allocation_id"] = allocation_id
        return super().create(validated_data)


class TicketAttachmentUpdateSerializer(ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = fields = ("files",)

    def create(self, validated_data):
        ticket_id = self.context["ticket_id"]
        try:
            Ticket.objects.get(_id=ticket_id)
        except Ticket.DoesNotExist:
            raise ValidationError("Ticket doesn't Exist")

        validated_data["ticket_id"] = ticket_id
        return super().create(validated_data)
