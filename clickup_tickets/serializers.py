from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.serializers import CharField, DateField
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
from clickup_utils.validators import check_name, check_date_below


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
    createdBy = TicketEmployeeSerializer(many=True)
    updatedBy = TicketEmployeeSerializer(many=True)
    deletedBy = TicketEmployeeSerializer(many=True)

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
    title = CharField(validators=[check_name])
    description = CharField(max_length=500)
    startDate = DateField(validators=[check_date_below])

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

        allocation.createdBy.add(self.context.get("request").user.employee)
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

        instance.updatedBy.add(self.context.get("request").user.employee)

        if validated_data.get("assignedUsers"):
            assigned_users_data = validated_data.get("assignedUsers")
            instance.assignedUsers.clear()
            for user in assigned_users_data:
                team_member = TeamMember.objects.get(**user)
                instance.assignedUsers.add(team_member)

        return instance

    def validate_assignedUsers(self, value):
        for user in value:
            try:
                TeamMember.objects.get(_id=user["_id"])
            except TeamMember.DoesNotExist:
                raise ValidationError("TeamMember Doesn't Exist " + user["_id"])
        return value

    def validate(self, data):
        start_date = data.get("startDate", self.instance.startDate)
        due_date = data.get("dueDate", self.instance.dueDate)
        if due_date and start_date:
            if due_date < start_date:
                raise ValidationError("Due date should be greater than Start date.")

        return super().validate(data)


class TicketSerializer(ModelSerializer):
    allocations = TicketAllocationSerializer(many=True)
    createdBy = TicketEmployeeSerializer(many=True)
    updatedBy = TicketEmployeeSerializer(many=True)
    deletedBy = TicketEmployeeSerializer(many=True)

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
    title = CharField(validators=[check_name])
    description = CharField(max_length=500)
    startDate = DateField(validators=[check_date_below])

    class Meta:
        model = Ticket
        fields = (
            "title",
            "description",
            "startDate",
            "dueDate",
            "priority",
        )
    
    def update(self, instance, validated_data):
        instance.updatedBy.add(self.context.get("request").user.employee)
        return super().update(instance, validated_data)

    def validate(self, data):
        start_date = data.get("startDate", self.instance.startDate)
        due_date = data.get("dueDate", self.instance.dueDate)
        if due_date and start_date:
            if due_date < start_date:
                raise ValidationError("Due date should be greater than Start date.")

        return super().validate(data)


class TicketAllocationAttachmentUpdateSerializer(ModelSerializer):
    class Meta:
        model = TicketAllocationAttachment
        fields = ("files",)

    def create(self, validated_data):
        validated_data["ticket_allocation_id"] = self.context["allocation_id"]
        return super().create(validated_data)

    def validate(self, data):
        allocation_id = self.context["allocation_id"]
        try:
            TicketAllocation.objects.get(_id=allocation_id)
        except TicketAllocation.DoesNotExist:
            raise ValidationError("Ticket Allocation doesn't Exist")
        return super().validate(data)


class TicketAttachmentUpdateSerializer(ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = fields = ("files",)

    def create(self, validated_data):
        validated_data["ticket_id"] = self.context["ticket_id"]
        return super().create(validated_data)

    def validate(self, data):
        ticket_id = self.context["ticket_id"]
        try:
            Ticket.objects.get(_id=ticket_id)
        except Ticket.DoesNotExist:
            raise ValidationError("Ticket doesn't Exist")
        return super().validate(data)
