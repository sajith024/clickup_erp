from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.serializers import CharField

from .models import (
    Priority,
    TicketStatus,
    TicketAllocation,
    Ticket,
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
