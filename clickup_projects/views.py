from datetime import datetime, timedelta

from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_204_NO_CONTENT,
)
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
)

from .models import (
    Lists,
    Jokes,
    Sprints,
    Folders,
    Project,
    ProjectIcons,
    Role,
    Employee,
    TeamMember,
)

from .serializers import (
    ListsSerializer,
    ListsUpdateSerializer,
    JokesSerializer,
    SprintsSerializer,
    SprintAddSerializer,
    FoldersSerializer,
    FoldersBulkUpdateSerializer,
    FoldersUpdateSerializer,
    ProjectSerializer,
    ProjectIconsSerializer,
    RoleSerializer,
    EmployeeSerializer,
    TeamMemberSerializer,
)


# Create your views here.
@extend_schema_view()
class ListsViewSet(ModelViewSet):
    queryset = Lists.objects.all()
    serializer_class = ListsSerializer
    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListsSerializer
        elif self.request.method == "POST" and self.request.data.get("folder"):
            return FoldersUpdateSerializer

        return ListsUpdateSerializer

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == HTTP_204_NO_CONTENT:
            response.status_code = HTTP_200_OK
        return response


class JokesView(ListAPIView):
    serializer_class = JokesSerializer

    def get_queryset(self):
        return Jokes.objects.order_by("?").first()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset)
        return Response(
            {
                "data": serializer.data["joke"],
                "message": "Jokes Fetched Successfully",
            }
        )


@extend_schema_view()
class SprintsViewSet(ModelViewSet):
    queryset = Sprints.objects.all()
    serializer_class = SprintsSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SprintAddSerializer

        return SprintsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        project_id = validated_data.get("project")
        number_of_sprint = validated_data.get("numberOfSprints")
        sprint_duration = validated_data.get("sprintDuration")
        start_date_data = validated_data.get("startDate")

        try:
            project = Project.objects.get(_id=project_id)
        except Project.DoesNotExist:
            raise Response("Project doesn't Exist.", HTTP_400_BAD_REQUEST)

        sprint_list = []
        start_date = start_date_data.date()
        last_sprint = project.sprint.order_by("created_at").last()
        if last_sprint:
            last_sprint_no = int(last_sprint.name.split(" ")[1])
        else:
            last_sprint_no = 0
        for i in range(number_of_sprint):
            end_date = self.skip_weekend(start_date, sprint_duration)
            last_sprint_no += 1
            sprint = Sprints.objects.create(
                name=f"Sprint {last_sprint_no} ({start_date.strftime('%d-%m-%Y')}/{end_date.strftime('%d-%m-%Y')})",
                project=project,
            )
            sprint_list.append(sprint)
            start_date = end_date + timedelta(days=1)

        response = SprintsSerializer(data=sprint_list, many=True)
        response.is_valid()
        return Response(response.data, status=HTTP_201_CREATED)

    def skip_weekend(self, start_date, sprint_duration):
        end_date = start_date
        for i in range(sprint_duration - 1):
            date = end_date + timedelta(days=1)
            while date.weekday() in [5, 6]:
                date += timedelta(days=1)
            end_date = date
        return end_date

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == HTTP_204_NO_CONTENT:
            response.status_code = HTTP_200_OK
        return response


@extend_schema_view()
class FoldersViewSet(ModelViewSet):
    queryset = Folders.objects.all()
    serializer_class = FoldersSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return FoldersSerializer

        return FoldersBulkUpdateSerializer

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == HTTP_204_NO_CONTENT:
            response.status_code = HTTP_200_OK
        return response


@extend_schema_view()
class ProjectView(ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view()
class ProjectIconsView(ListAPIView):
    queryset = ProjectIcons.objects.all()
    serializer_class = ProjectIconsSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {"colors": response.data, "icons": []}
        return response


@extend_schema_view()
class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view()
class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view()
class TeamMemberView(CreateAPIView):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        params = self.request.data.get("params", {})
        project_id = params.get("projectId")
        if project_id:
            return TeamMember.objects.filter(project___id=project_id)
        else:
            return self.queryset.all()

    def create(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "allocatedUsers": {
                    "projectAggregation": serializer.data,
                    "totalAllocatedUsers": len(serializer.data),
                }
            },
            HTTP_200_OK,
        )
