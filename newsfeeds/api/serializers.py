from rest_framework import serializers
from newsfeeds.models import NewsFeed
from accounts.api.serializers import UserSerializerForNewsfeed
from tweets.api.serializers import TweetSerializerForNewsfeed

class NewsfeedSerializer(serializers.ModelSerializer):

    user = UserSerializerForNewsfeed()
    tweet = TweetSerializerForNewsfeed()

    class Meta:
        model = NewsFeed
        fields = ('id', 'user', 'tweet', 'created_at' )
