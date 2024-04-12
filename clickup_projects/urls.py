from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ListsViewSet,
    JokesView,
    SprintsViewSet,
    FoldersViewSet,
    ProjectView,
    ProjectIconsView,
    RoleViewSet,
    EmployeeViewSet,
    TeamMemberView,
)


router = DefaultRouter()
router.register("list", ListsViewSet, basename="list")
router.register("sprint", SprintsViewSet, basename="sprint")
router.register("folder", FoldersViewSet, basename="folder")
router.register("role", RoleViewSet, basename="role")
router.register("employee", EmployeeViewSet, basename="employee")

urlpatterns = [
    path("jokes", JokesView.as_view(), name="jokes"),
    path("projectIcons", ProjectIconsView.as_view(), name="projectIcons"),
    path("project/list", ProjectView.as_view(), name="project"),
    path("team-member", TeamMemberView.as_view(), name="team-member"),
    path("", include(router.urls)),
]
