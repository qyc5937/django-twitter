from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from rest_framework.validators import ValidationError
from likes.models import Like
from comments.models import Comment
from tweets.models import Tweet
from accounts.api.serializers import UserSerializer
from comments.api.serializers import CommentSerializer

class LikeSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model =  Like
        fields = ('id', 'user', 'created_at', 'content_type', 'object_id')

class BaseLikeSerializerForCreateAndCancel(serializers.ModelSerializer):

    content_type = serializers.ChoiceField(choices=['comment','tweet'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id')

    def _get_model_class(self, data):
        if data['content_type'] == 'comment':
            return Comment
        elif data['content_type'] == 'tweet':
            return Tweet
        return None

    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise ValidationError({'content_type': 'Content type does not exists.'})
        liked_object = model_class.objects.filter(id=data['object_id']).first()
        if not liked_object:
            raise ValidationError({"object_id": "Object does not exists."})
        return data

class LikeSerializerForCreate(BaseLikeSerializerForCreateAndCancel):

    def create(self, validated_data):
        user = self.context['request'].user
        content_type = ContentType.objects.get_for_model(self._get_model_class(validated_data))
        object_id = validated_data['object_id']
        like, _ = Like.objects.get_or_create(user=user, content_type=content_type, object_id=object_id)
        return like

class LikeSerializerForCancel(BaseLikeSerializerForCreateAndCancel):

    def cancel(self):
        Like.objects.filter(
            user = self.context['request'].user,
            content_type= ContentType.objects.get_for_model(self._get_model_class(self.validated_data)),
            object_id = self.validated_data['object_id']
        ).delete()