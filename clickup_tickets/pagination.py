from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ClickUpTicketPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"

    def get_paginated_response(self, data):
        data[0].update(
            {
                "pagination": {
                    "page": self.page.number,
                    "limit": self.page.paginator.per_page,
                }
            }
        )
        return Response(data)
