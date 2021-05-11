from rest_framework import serializers
from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializerForNewsfeed

class NewsfeedSerializer(serializers.ModelSerializer):

    tweet = TweetSerializerForNewsfeed()

    class Meta:
        model = NewsFeed
        fields = ('id', 'tweet', 'created_at' )
