from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from utils.constants import MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE

class FriendshipPagination(PageNumberPagination):

    #allow customization of default page size as a param
    page_size_query_param = 'size'
    page_size = DEFAULT_PAGE_SIZE
    max_page_size = MAX_PAGE_SIZE

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_pages': self.page.has_next(),
            'results': data,
        })