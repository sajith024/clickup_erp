from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ClickUpTicketPagination(PageNumberPagination):
    page_size_query_param = "limit"

    def get_page_number(self, request, paginator):
        params = self.request.data.get("params", {})
        page_number = params.get("page", 1)
        return page_number

    def get_paginated_response(self, data):
        return Response(
            {
                "pagination": {
                    "page": self.page.number,
                    "limit": self.page.paginator.per_page,
                },
                "data": data,
            }
        )
