from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from tweets.models import Tweet
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from newsfeeds.services import NewsFeedService

class TweetViewSet(viewsets.GenericViewSet):

    '''
    API Endpoints for creating and listing tweets
    '''

    serializer_class = TweetSerializerForCreate


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
            }, status=HTTP_400_BAD_REQUEST)

        tweet = serialzier.save()
        #fan out to followers
        NewsFeedService.fan_out_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=HTTP_201_CREATED)


    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response('Invalid user_id', status=HTTP_400_BAD_REQUEST)

        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        return Response({"tweets": serializer.data})