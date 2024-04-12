from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
)

from clickup_projects.pagination import ClickUpPagination
from .pagination import ClickUpTicketPagination

from .models import (
    Priority,
    TicketStatus,
    TicketAllocation,
    Ticket,
)

from .serializers import (
    PrioritySerializer,
    TicketStatusSerializer,
    TicketAllocationSerializer,
    TicketGroupSerializer,
)


# Create your views here.
@extend_schema_view()
class PriorityView(ListAPIView):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    permission_classes = []

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {"priority": response.data}
        return response


@extend_schema_view()
class TicketStatusView(ListAPIView):
    queryset = TicketStatus.objects.all()
    serializer_class = TicketStatusSerializer
    permission_classes = []
    pagination_class = ClickUpPagination

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "status": response.data["data"],
            "pagination": response.data["pagination"],
        }
        return response


@extend_schema_view()
class TicketAllocationViewSet(ModelViewSet):
    queryset = TicketAllocation.objects.all()
    serializer_class = TicketAllocationSerializer
    permission_classes = []


@extend_schema_view()
class TicketView(CreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketGroupSerializer
    pagination_class = ClickUpTicketPagination
    permission_classes = []

    def get_queryset(self):
        params = self.request.data.get("params", {})
        list_id = params.get("listId")
        sprint_id = params.get("sprintId")
        statuses = TicketStatus.objects.all()

        queryset_list = []
        if list_id:
            tickets = Ticket.objects.filter(list___id=list_id)
        elif sprint_id:
            tickets = Ticket.objects.filter(sprint___id=sprint_id)
        else:
            tickets = Ticket.objects.all()

        allocations = TicketAllocation.objects.filter(ticket__in=tickets)
        for status in statuses:
            ticket = tickets.prefetch_related(
                Prefetch(
                    "allocations", queryset=allocations.filter(ticketStatus=status)
                )
            ).filter(allocations__ticketStatus=status)
            if ticket:
                queryset_list.append(
                    {
                        "_id": status._id,
                        "groupById": status._id,
                        "data": ticket,
                    }
                )

        return queryset_list

    def create(self, request, *args, **kwargs):
        params = request.data.get("params", {})
        self.pagination_class.page_size = params.get("limit", 10)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)

        data = {
            "ticketData": response.data["data"],
            "pagination": response.data["pagination"],
            "totalCount": [{"count": len(x["data"])} for x in response.data["data"]],
        }
        return Response(data, status=HTTP_200_OK)
