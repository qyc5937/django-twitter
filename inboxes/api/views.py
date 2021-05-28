from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from inboxes.api.serializers import NotificationSerializer, NotificationSerializerForUpdate
from notifications.models import Notification
from utils.decorators import required_params

class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):

    '''
    API Endpoints for creating and listing tweets
    '''

    serializer_class = NotificationSerializerForUpdate
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated,]
    filterset_fields = ('unread',)

    def get_queryset(self):
        return self.request.user.notifications.all()

    @action(methods=['GET'], detail=False, url_path='unread-count')
    def unread_count(self, request, *args, **kwargs):
        '''
        return number of unread notifications for the logged in user
        '''
        return Response({
            "success": True,
            "unread_count": self.get_queryset().filter(unread=True).count()
        }, status=HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        '''
        mark all of logged in user's notification as read
        '''

        updated_count = self.get_queryset().update(unread=False)
        return Response({
            "updated_count": updated_count,
            "success": True,
        }, HTTP_200_OK)

    @required_params(method='POST', params=['unread'])
    def update(self, request, *args, **kwargs):
        '''
        mark notification message as read/unread
        '''
        serializer = NotificationSerializerForUpdate(
            instance=self.get_object(),
            data=request.data
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=HTTP_400_BAD_REQUEST)
        notification = serializer.save()
        return Response(
            NotificationSerializer(notification).data
        , status=HTTP_200_OK)