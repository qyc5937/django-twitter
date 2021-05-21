from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer, CommentSerializerWithLikes
from likes.api.serializers import LikeSerializer

class TweetSerializer(serializers.ModelSerializer):

    user = UserSerializerForTweet()

    class Meta:
        model =  Tweet
        fields = ('id', 'user', 'created_at', 'content')

class TweetSerializerForCreate(serializers.ModelSerializer):

    content = serializers.CharField(min_length=6, max_length=255)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet

class TweetSerializerForNewsfeed(serializers.ModelSerializer):

    class Meta:
        model = Tweet
        fields = ('id','content',)

class TweetSerializersWithCommentsAndLikes(serializers.ModelSerializer):
    user = UserSerializerForTweet()
    comments = CommentSerializerWithLikes(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'content', 'comments', 'likes', 'created_at')