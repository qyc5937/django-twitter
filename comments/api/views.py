from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import *
from comments.api.serializers import CommentSerializerForCreate, CommentSerializer
from comments.models import Comment
from utils.decorators import required_params

class CommentViewSet(viewsets.GenericViewSet):

    '''
    API Endpoints for creating and listing tweets
    '''

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    def create(self, request):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data['tweet_id'],
            'content': request.data['content'],
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
        return Response()

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_params(params=['tweet_id'])
    def list(self, request):
        comments = Comment.objects.filter(
            tweet_id=request.query_params['tweet_id']
        ).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({
            "success": True,
            "comments": serializer.data,
        }, status=HTTP_200_OK)
