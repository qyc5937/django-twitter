from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import *
from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
    CommentSerializerForUpdate,
    CommentSerializerWithLikes,
)
from comments.models import Comment
from utils.decorators import required_params
from utils.permissions import IsObjectOwner
from inboxes.services import NotificationService

class CommentViewSet(viewsets.GenericViewSet):
    '''
    API Endpoints for creating and listing tweets
    '''

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)
    def create(self, request):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        serialzier = CommentSerializerForCreate(
            data=data,
            context={'request': request},
        )

        if not serialzier.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serialzier.errors,
            }, status=HTTP_400_BAD_REQUEST)

        comment = serialzier.save()
        #send out notifications
        NotificationService.send_comment_notification(comment)
        return Response(CommentSerializer(comment, context={'request': request}).data, status = HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        return Response({'success': True}, status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):

        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check inputs.",
                "errors": serializer.errors,
            }, status=HTTP_400_BAD_REQUEST)
        comment = serializer.save()

        return Response(CommentSerializer(comment).data, status=HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        elif self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [IsAuthenticated()]

    @required_params(method='GET', params=['tweet_id'])
    def list(self, request):
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset)\
            .prefetch_related('user')\
            .order_by('-created_at')
        serializer = CommentSerializerWithLikes(
            comments,
            context={'request': request},
            many=True,
        )
        return Response({
            "success": True,
            "comments": serializer.data,
        }, status=HTTP_200_OK)
