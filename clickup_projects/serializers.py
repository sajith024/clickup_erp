from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.serializers import (
    SerializerMethodField,
    CharField,
    ImageField,
    IntegerField,
    DateTimeField,
    ListField,
)

from rest_framework.serializers import ValidationError

from clickup_utils.validators import check_name, check_date_range

from .models import (
    Lists,
    Jokes,
    Sprints,
    Folders,
    Project,
    ProjectIcons,
    Role,
    Department,
    Skill,
    Education,
    Employee,
    TeamMember,
)


class ListsSerializer(ModelSerializer):
    ticketCount = SerializerMethodField()
    class Meta:
        model = Lists
        fields = (
            "_id",
            "name",
            "ticketCount"
        )
        
    def get_ticketCount(self, list):
        return list.ticket_list.count()


class ListsUpdateSerializer(ModelSerializer):
    name = CharField(validators=[check_name])

    class Meta:
        model = Lists
        fields = (
            "name",
            "project",
        )


class JokesSerializer(ModelSerializer):
    class Meta:
        model = Jokes
        fields = ("joke",)


class SprintsSerializer(ModelSerializer):
    ticketCounts = SerializerMethodField()
    class Meta:
        model = Sprints
        fields = (
            "_id",
            "name",
            "active",
            "status",
            "ticketCounts",
        )
        
    def get_ticketCounts(self, sprint):
        return sprint.ticket_sprint.count()

class SprintAddSerializer(Serializer):
    project = CharField()
    numberOfSprints = IntegerField()
    sprintDuration = IntegerField()
    startDate = DateTimeField(validators=[check_date_range])


class FoldersSerializer(ModelSerializer):
    list = ListsSerializer(many=True)

    class Meta:
        model = Folders
        fields = (
            "_id",
            "name",
            "list",
        )


class FoldersBulkUpdateSerializer(ModelSerializer):
    name = CharField(validators=[check_name])
    lists = ListField(child=CharField(), source="list.name")

    class Meta:
        model = Folders
        fields = (
            "_id",
            "name",
            "project",
            "lists",
        )

    def create(self, validated_data):
        lists = validated_data.pop("list").get("name")
        project = validated_data.get("project")
        folder = Folders.objects.create(**validated_data)
        for list_name in lists:
            folder_list = Lists.objects.create(name=list_name, project=project)
            folder.list.add(folder_list)
        return folder


class FoldersUpdateSerializer(ModelSerializer):
    folder = CharField(source="_id")
    name = CharField(source="list.name", validators=[check_name])

    class Meta:
        model = Folders
        fields = (
            "folder",
            "project",
            "name",
        )

    def create(self, validated_data):
        lists = validated_data.pop("list").get("name")
        project = validated_data.get("project")
        folder_id = validated_data.get("_id")
        folder = Folders.objects.get(_id=folder_id)
        folder_list = Lists.objects.create(name=lists, project=project)
        folder.list.add(folder_list)
        return folder

    def validate_folder(self, value):
        try:
            Folders.objects.get(_id=value)
        except Folders.DoesNotExist:
            raise ValidationError("Folder Doesn't Exist")

        return value


class ProjectSerializer(ModelSerializer):
    name = CharField(validators=[check_name])
    sprint = SprintsSerializer(many=True)
    folders = SerializerMethodField()
    lists = SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "_id",
            "name",
            "erpId",
            "shortCode",
            "logo",
            "sprint",
            "folders",
            "lists",
        )

    def get_folders(self, project):
        folders = project.folders.all()
        return FoldersSerializer(folders, many=True).data

    def get_lists(self, project):
        all_lists = project.lists.all()
        lists_in_folders = project.lists.filter(folders__isnull=False).distinct()
        lists_not_in_folder = all_lists.exclude(
            _id__in=lists_in_folders.values_list("_id", flat=True),
        )
        return ListsSerializer(lists_not_in_folder, many=True).data


class ProjectIconsSerializer(ModelSerializer):
    class Meta:
        model = ProjectIcons
        fields = "__all__"


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class DepartmentSerializer(ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class SkillSerializer(ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class EducationSerializer(ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


class TeamMemberSerializer(ModelSerializer):
    userId = CharField(source="user._id")
    role = CharField(source="user.role._id")
    user = CharField(source="user.user.get_full_name")
    employeeName = CharField(source="user.user.get_full_name")
    photo = ImageField(source="user.photo")
    allocationHours = SerializerMethodField()
    department = CharField(source="user.role.department.name")
    roleName = CharField(source="user.role.name")
    totalTickets = IntegerField(default=0)
    todo = IntegerField(default=0)
    inprogress = IntegerField(default=0)
    completed = IntegerField(default=0)
    readyforQA = IntegerField(default=0)
    ticketsFirstApproved = IntegerField(default=0)
    rejectionCount = IntegerField(default=0)
    performanceIndex = IntegerField(default=0)
    qualityIndex = IntegerField(default=0)

    class Meta:
        model = TeamMember
        fields = (
            "_id",
            "userId",
            "role",
            "user",
            "employeeName",
            "photo",
            "allocationHours",
            "department",
            "roleName",
            "totalTickets",
            "todo",
            "inprogress",
            "completed",
            "readyforQA",
            "ticketsFirstApproved",
            "rejectionCount",
            "lastWorked",
            "performanceIndex",
            "qualityIndex",
        )

    def get_allocationHours(self, team_member):
        total_seconds = team_member.allocationHours.total_seconds()
        return int(total_seconds // 3600)
