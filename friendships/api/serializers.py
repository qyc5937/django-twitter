from rest_framework import serializers
from friendships.models import Friendship
from accounts.api.serializers import UserSerializerForFriendship
from rest_framework.validators import ValidationError

class FollowerSerializer(serializers.ModelSerializer):

    user = UserSerializerForFriendship(source='from_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at',)

class FollowingSerializer(serializers.ModelSerializer):

    user = UserSerializerForFriendship(source='to_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at',)

'''class FriendshipSerializer(serializers.ModelSerializer):

    user = UserSerializerForFriendship()

    class Meta:
        model = Friendship
        fields = ('id', 'from_user', 'to_user', 'created_at',)
'''

class FriendshipSerializerForCreate(serializers.ModelSerializer):

    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'Follower and followee must be different.'
            })
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )
