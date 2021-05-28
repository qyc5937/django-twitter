from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from tweets.models import Tweet
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializersWithCommentsAndLikes,
)
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params
from utils.constants import *

class TweetViewSet(viewsets.GenericViewSet):

    '''
    API Endpoints for creating and listing tweets
    '''

    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()

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
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_params(method='GET', params=['user_id'] )
    def list(self, request, *args, **kwargs):
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializersWithCommentsAndLikes(
            tweets,
            context= {'request': request},
            many=True,
        )
        return Response({"tweets": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        tweet_with_comments = TweetSerializersWithCommentsAndLikes(
            tweet,
            context= {'request': request},
        ).data
        all_comments = tweet_with_comments['comments'][:]
        tweet_with_comments['comments'] = all_comments[:DEFAULT_COMMENT_DISPLAY_NUM]
        if 'with_all_comments' in request.query_params and request.query_params['with_all_comments']:
            tweet_with_comments['comments'] = all_comments
        if 'with_preview_comments' in request.query_params and request.query_params['with_preview_comments']:
            tweet_with_comments['comments'] = all_comments[:PREVIEW_COMMENT_DISPLAY_NUM]
        return Response(tweet_with_comments)