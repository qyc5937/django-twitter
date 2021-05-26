from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer, CommentSerializerWithLikes
from likes.api.serializers import LikeSerializer
from likes.services import LikeService

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
    has_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'content',
            'comments',
            'likes',
            'has_liked',
            'likes_count',
            'comments_count',
            'created_at',
        )

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_likes_count(self, obj):
        return obj.like_set.count()