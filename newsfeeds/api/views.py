from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsfeedSerializer

class NewsFeedViewSet(viewsets.GenericViewSet):

    '''
    API Endpoints for creating and listing tweets
    '''

    serializer_class = NewsfeedSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        newsfeeds = NewsFeed.objects.filter(user_id=self.request.user)
        return Response({
            'newsfeed': NewsfeedSerializer(
                newsfeeds,
                many=True).data
        }, status=HTTP_200_OK)