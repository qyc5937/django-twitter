from rest_framework import serializers
from accounts.api.serializers import UserSerializer
from notifications.models import Notification
class NotificationSerializer(serializers.ModelSerializer):

    recipient = UserSerializer()

    class Meta:
        model =  Notification
        fields = (
            'id',
            'recipient',
            'actor_content_type',
            'actor_object_id',
            'action_object_content_type',
            'action_object_object_id',
            'target_content_type_id',
            'target_object_id',
            'verb',
            'deleted',
            'timestamp',
            'unread',
            'description',
        )
class NotificationSerializerForUpdate(serializers.ModelSerializer):

    unread = serializers.BooleanField()

    class Meta:
        model = Notification
        fields = ('id', 'unread',)

    def update(self, instance, validated_data):
        instance.unread = validated_data['unread']
        instance.save()
        return instance
