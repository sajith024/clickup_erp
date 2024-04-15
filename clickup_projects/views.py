from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
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
    FoldersSerializer,
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

        return ListsUpdateSerializer


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


@extend_schema_view()
class FoldersViewSet(ModelViewSet):
    queryset = Folders.objects.all()
    serializer_class = FoldersSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == "GET":
            return FoldersSerializer

        return FoldersUpdateSerializer

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
