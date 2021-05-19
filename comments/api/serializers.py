from rest_framework import serializers
from rest_framework.validators import ValidationError
from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from tweets.models import Tweet

class CommentSerializer(serializers.ModelSerializer):

    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = ('id', 'tweet_id', 'user', 'content', 'created_at')

class CommentSerializerForCreate(serializers.ModelSerializer):

    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    content = serializers.CharField(min_length=6, max_length=140)

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