from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST,HTTP_401_UNAUTHORIZED
from rest_framework import permissions
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowerSerializer,
#    FriendshipSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)
import logging

class FriendshipViewSet(viewsets.GenericViewSet):

    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        if not pk:
            return Response('Invalid user',HTTP_401_UNAUTHORIZED)
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        return Response(FollowerSerializer(friendships,many=True).data, status=HTTP_200_OK)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        if not pk:
            return Response('Invalid user',HTTP_401_UNAUTHORIZED)
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        return Response({'followings': FollowingSerializer(friendships,many=True).data}, status=HTTP_200_OK)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):

        #check if follow user exists
        self.get_object()
        if Friendship.objects.filter(from_user=request.user,to_user=pk):
            return Response({
                "success": True,
                "duplicate": True,
            }, HTTP_201_CREATED)
        if not User.objects.filter(id=pk).exists():
            logging.error(pk)
            logging.error(User.objects.filter(id=pk).exists())
            return Response({
                "success": False,
            }, HTTP_400_BAD_REQUEST)

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Invalid inputs.",
                "error": serializer.errors,
            }, HTTP_400_BAD_REQUEST)
        friendship = serializer.save()
        return Response({
            FriendshipSerializerForCreate(friendship).data,
        }, status=HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):

        unfollow_user = self.get_object()
        if request.user.id == unfollow_user.id:
            return Response({
                "success": False,
                "message": "You cannot unfollow yourself."
            }, status=HTTP_400_BAD_REQUEST)
        friendship = Friendship.objects.filter(from_user=request.user,to_user_id=pk)
        deleted, _ = friendship.delete()
        return Response({
            "success": True,
            "deleted": deleted
        }, status=HTTP_200_OK)

    def list(self, request):
        return Response({"message": "default page for friendship api"})