from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    PriorityView,
    TicketStatusView,
    TicketAllocationViewSet,
    TicketViewSet,
    TicketAllocationAttachmentView,
    TicketAttachmentView,
)


router = DefaultRouter()
router.register(
    "ticket-allocation", TicketAllocationViewSet, basename="ticket-allocation"
)
router.register("ticket", TicketViewSet, basename="ticket")

urlpatterns = [
    path("priority", PriorityView.as_view(), name="priority"),
    path("ticketStatus", TicketStatusView.as_view(), name="ticketStatus"),
    re_path(
        r"ticket-allocation/attachment/(?P<pk>[0-9a-f-]+)",
        TicketAllocationAttachmentView.as_view(),
        name="ticket_allocation_attachment",
    ),
    re_path(
        r"ticket/attachment/(?P<pk>[0-9a-f-]+)",
        TicketAttachmentView.as_view(),
        name="ticket_attachment",
    ),
    path("", include(router.urls)),
]
