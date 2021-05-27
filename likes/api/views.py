from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from likes.models import Like
from likes.api.serializers import (
    LikeSerializer,
    LikeSerializerForCreate,
    LikeSerializerForCancel,
)
from utils.decorators import required_params
from inboxes.services import NotificationService

class LikeViewSet(viewsets.GenericViewSet):

    '''
    API Endpoints for creating and listing tweets
    '''

    serializer_class = LikeSerializerForCreate
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]

    @required_params(request_attr='data', params=['content_type', 'object_id'])
    def create(self, request):
        serialzier = LikeSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serialzier.is_valid():
            return Response({
               "success": False,
               "message": "Please check input.",
               "errors": serialzier.errors,
            }, status=HTTP_400_BAD_REQUEST)

        like = serialzier.save()
        #send like notification
        NotificationService.send_like_notificaion(like)
        return Response(LikeSerializer(like).data, status=HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    @required_params(request_attr='data', params=['content_type', 'object_id'])
    def cancel(self, request, *args, **kwargs):
        '''
        method use for unliking a tweet/comment
        /api/likes/cancel
        '''
        serializer = LikeSerializerForCancel(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors,
            }, status=HTTP_400_BAD_REQUEST)
        serializer.cancel()
        return Response({'success': True}, status=HTTP_200_OK)
