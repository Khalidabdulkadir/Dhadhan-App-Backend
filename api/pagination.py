from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class OptionalPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_query_param = 'page'
    page_size = 10
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        # If no page param sent — skip pagination entirely
        if 'page' not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'pagination': {
                'currentPage': self.page.number,
                'totalPages': self.page.paginator.num_pages,
                'totalCount': self.page.paginator.count,
                'hasNextPage': self.get_next_link() is not None,
                'limit': self.get_page_size(self.request)
            }
        })