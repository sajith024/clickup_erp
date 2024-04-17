from rest_framework.generics import (
    ListAPIView,
    UpdateAPIView,
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch, Count

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
    TicketAllocationAttachment,
    TicketAttachment,
)

from .serializers import (
    PrioritySerializer,
    TicketStatusSerializer,
    TicketAllocationSerializer,
    TicketAllocationUpdateSerializer,
    TicketGroupSerializer,
    TicketUpdateSerializer,
    TicketAllocationAttachmentUpdateSerializer,
    TicketAttachmentUpdateSerializer,
)


# Create your views here.
@extend_schema_view()
class PriorityView(ListAPIView):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {"priority": response.data}
        return response


@extend_schema_view()
class TicketStatusView(ListAPIView):
    queryset = TicketStatus.objects.order_by("title").all()
    serializer_class = TicketStatusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClickUpPagination

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "status": response.data["data"],
            "pagination": response.data["pagination"],
        }
        return response


@extend_schema_view()
class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketUpdateSerializer
    pagination_class = ClickUpTicketPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        list_id = self.request.query_params.get("listId")
        sprint_id = self.request.query_params.get("sprintId")
        data_count = self.request.query_params.get("dataCount", 0)

        try:
            data_count = int(data_count)
        except TypeError:
            data_count = 0

        if list_id or sprint_id:
            tickets = Ticket.objects.filter(list_id=list_id, sprint_id=sprint_id)
            allocations = TicketAllocation.objects.filter(ticket__in=tickets)
            ticket_group_by = (
                allocations.values("ticketStatus", "ticketStatus__title")
                .annotate(
                    ticket_count=Count("ticketStatus"),
                )
                .order_by()
            )
            if ticket_group_by.exists():
                status_id = ticket_group_by[data_count]["ticketStatus"]
                status_name = ticket_group_by[data_count]["ticketStatus__title"]
                ticket = tickets.prefetch_related(
                    Prefetch(
                        "allocations",
                        queryset=allocations.filter(ticketStatus=status_id),
                    )
                ).filter(allocations__ticketStatus=status_id)

                return [
                    {
                        "ticketData": [
                            {
                                "_id": status_id,
                                "groupById": status_id,
                                "data": ticket,
                            }
                        ],
                        "TableHeading": {
                            "_id": status_id,
                            "name": status_name,
                        },
                        "totalCount": [
                            {"count": group["ticket_count"]}
                            for group in ticket_group_by
                        ],
                    }
                ]
            else:
                return [
                    {
                        "ticketData": [],
                        "pagination": {},
                        "TableHeading": {},
                        "totalCount": [],
                    }
                ]

        return self.queryset.all()

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.query_params.get("listId") or self.request.query_params.get(
            "sprintId"
        ):
            serializer_class = TicketGroupSerializer

        return serializer_class

    def list(self, request, *args, **kwargs):
        if request.query_params.get("listId") or request.query_params.get("sprintId"):
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return Response(response.data[0], status=HTTP_200_OK)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == HTTP_204_NO_CONTENT:
            response.status_code = HTTP_200_OK
        return response


@extend_schema_view()
class TicketAllocationViewSet(ModelViewSet):
    queryset = TicketAllocation.objects.all()
    serializer_class = TicketAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method != "GET":
            return TicketAllocationUpdateSerializer
        return self.serializer_class

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == HTTP_204_NO_CONTENT:
            response.status_code = HTTP_200_OK
        return response


@extend_schema_view()
class TicketAllocationAttachmentView(UpdateAPIView):
    queryset = TicketAllocationAttachment.objects.all()
    serializer_class = TicketAllocationAttachmentUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["allocation_id"] = self.kwargs.get("pk")
        return context

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


@extend_schema_view()
class TicketAttachmentView(UpdateAPIView):
    queryset = TicketAttachment.objects.all()
    serializer_class = TicketAttachmentUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["ticket_id"] = self.kwargs.get("pk")
        return context

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
