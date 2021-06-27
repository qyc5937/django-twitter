from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsfeedSerializer
from utils.paginations import EndlessPagination

class NewsFeedViewSet(viewsets.GenericViewSet):

    '''
    API Endpoints for creating and listing tweets
    '''

    serializer_class = NewsfeedSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def get_queryset(self):
        queryset = NewsFeed.objects.filter(user=self.request.user)
#        for q in queryset:
#            print("data from queryset!!!! ", q, '\n')
#        print('----------------')
        return queryset

    def list(self, request):
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = NewsfeedSerializer(
            queryset,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)
