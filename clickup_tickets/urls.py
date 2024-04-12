from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PriorityView,
    TicketStatusView,
    TicketAllocationViewSet,
    TicketView,
)


router = DefaultRouter()
router.register(
    "ticket-allocation", TicketAllocationViewSet, basename="ticket-allocation"
)

urlpatterns = [
    path("priority", PriorityView.as_view(), name="priority"),
    path("ticketStatus", TicketStatusView.as_view(), name="ticketStatus"),
    path("ticket", TicketView.as_view(), name="ticket"),
    path("", include(router.urls)),
]
