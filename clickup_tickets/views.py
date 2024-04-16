from rest_framework.generics import (
    ListAPIView,
    UpdateAPIView,
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
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
    queryset = TicketStatus.objects.all()
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
        statuses = TicketStatus.objects.all()

        queryset = Ticket.objects.all()
        if list_id or sprint_id:
            queryset_list = []
            if list_id:
                tickets = Ticket.objects.filter(list_id=list_id)
            elif sprint_id:
                tickets = Ticket.objects.filter(sprint_id=sprint_id)
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
                        {"_id": status._id, "groupById": status._id, "data": ticket}
                    )

            queryset = queryset_list

        return queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.query_params.get("listId") or self.request.query_params.get(
            "sprintId"
        ):
            serializer_class = TicketGroupSerializer

        return serializer_class

    def list(self, request, *args, **kwargs):
        if request.query_params.get("listId") or request.query_params.get("sprintId"):
            data_count = request.query_params.get("dataCount", 0)
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

            if response.data["data"]:
                ticket_data = response.data["data"][int(data_count)]
                status = TicketStatus.objects.get(_id=ticket_data["_id"])
                data = {
                    "ticketData": [ticket_data],
                    "pagination": response.data["pagination"],
                    "TableHeading": {
                        "_id": status._id,
                        "name": status.title,
                    },
                    "totalCount": [
                        {"count": len(x["data"])} for x in response.data["data"]
                    ],
                }
                return Response(data, status=HTTP_200_OK)
            else:
                return Response(
                    {
                        "ticketData": [],
                        "pagination": {},
                        "TableHeading": {},
                        "totalCount": [],
                    },
                    HTTP_200_OK,
                )
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
