from rest_framework import serializers
from friendships.models import Friendship
from accounts.api.serializers import UserSerializer

class FriendshipSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = Friendship
        fields = ('id', 'from_user', 'to_user', 'created_at')
