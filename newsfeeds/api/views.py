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
        return Response({'newsfeed': NewsfeedSerializer(newsfeeds, many=True).data}, status=HTTP_200_OK)
'''
    def create(self, request):
        serialzier = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )

        if not serialzier.is_valid():
            return Response({
               "success": False,
               "message": "Please check input.",
               "errors": serialzier.errors,
            }, status=400)

        tweet = serialzier.save()
        return Response(TweetSerializer(tweet).data, status=201)


    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response('Invalid user_id', status=400)

        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        r
'''