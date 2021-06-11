from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializerWithLikes
from rest_framework.exceptions import ValidationError
from tweets.constants import TWEET_PHOTO_MAX_NUM
from likes.api.serializers import LikeSerializer
from likes.services import LikeService
from tweets.services import TweetService

class TweetSerializer(serializers.ModelSerializer):

    user = UserSerializerForTweet()

    class Meta:
        model =  Tweet
        fields = ('id', 'user', 'created_at', 'content')

class TweetSerializerForCreate(serializers.ModelSerializer):

    content = serializers.CharField(min_length=6, max_length=255)
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True,
        required=False,
    )

    class Meta:
        model = Tweet
        fields = ('content', 'files',)

    def validate(self, data):
        if len(data.get('files',[])) > TWEET_PHOTO_MAX_NUM:
            raise ValidationError({
            "message": f'You can upload a maximum of {TWEET_PHOTO_MAX_NUM} photos.'
        })
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        if validated_data.get('files'):
            TweetService.create_tweet_photos(tweet, validated_data['files'])
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
    photo_urls = serializers.SerializerMethodField()

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
            'photo_urls',
            'created_at',
        )

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_photo_urls(self, obj):
        photo_urls = []
        for photo in obj.tweetphoto_set.all().order_by('order'):
            photo_urls.append(photo.file.url)
        return photo_urls