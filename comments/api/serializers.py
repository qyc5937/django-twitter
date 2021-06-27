from rest_framework import serializers
from utils.constants import *
from rest_framework.validators import ValidationError
from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from tweets.models import Tweet
from likes.api.serializers import LikeSerializer
from likes.services import LikeService

class CommentSerializer(serializers.ModelSerializer):

    user = UserSerializerForComment(source='cached_user')

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'user',
            'content',
            'created_at',
            'updated_at'
        )


class CommentSerializerForCreate(serializers.ModelSerializer):

    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    content = serializers.CharField(min_length=COMMENT_MIN_LENGTH, max_length=COMMENT_MAX_LENGTH)

    class Meta:
        model = Comment
        fields = ('tweet_id', 'user_id', 'content',)

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id):
            raise ValidationError("Tweet_id does not exists")
        return data

    def create(self, validated_data):
        user_id = validated_data['user_id']
        tweet_id = validated_data['tweet_id']
        content = validated_data['content']
        comment = Comment.objects.create(user_id=user_id,tweet_id=tweet_id,content=content)
        return comment

class CommentSerializerForUpdate(serializers.ModelSerializer):

    content = serializers.CharField(min_length=COMMENT_MIN_LENGTH, max_length=COMMENT_MAX_LENGTH)

    class Meta:
        model = Comment
        fields = ('content',)

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance

class CommentSerializerWithLikes(serializers.ModelSerializer):
    user = UserSerializerForComment(source='cached_user')
    likes = LikeSerializer(source='like_set', many=True)
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'user',
            'content',
            'likes_count',
            'has_liked',
            'likes',
            'created_at',
            'updated_at'
        )

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)