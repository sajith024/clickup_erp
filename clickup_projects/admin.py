from django.contrib import admin
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

# Register your models here.
admin.site.register(
    [
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
    ]
)
