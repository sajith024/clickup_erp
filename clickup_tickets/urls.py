from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PriorityView,
    TicketStatusView,
    TicketAllocationViewSet,
    TicketViewSet,
    TicketAllocationAttachmentViewSet,
    TicketAttachmentViewSet,
)


router = DefaultRouter()
router.register(
    "ticket-allocation", TicketAllocationViewSet, basename="ticket-allocation"
)
router.register("ticket", TicketViewSet, basename="ticket")
router.register(
    r"ticket-allocation/attachment/(?P<allocation_id>[0-9a-f-]+)",
    TicketAllocationAttachmentViewSet,
    basename="ticket_allocation_attachment",
)
router.register(
    r"ticket/attachment/(?P<ticket_id>[0-9a-f-]+)",
    TicketAttachmentViewSet,
    basename="ticket_attachment",
)

urlpatterns = [
    path("priority", PriorityView.as_view(), name="priority"),
    path("ticketStatus", TicketStatusView.as_view(), name="ticketStatus"),
    path("", include(router.urls)),
]
