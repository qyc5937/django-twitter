from testing.testcases import TestCase
from testing import testconstants
from notifications.models import Notification
from inboxes.services import NotificationService
from comments.models import Comment
from likes.models import Like
from rest_framework import status
# Create your tests here.
class InboxTest(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user_1=self.create_user("user1")
        self.user_2=self.create_user("user2")
        self.client_1 = self.login_user(self.user_1)
        self.client_2 = self.login_user(self.user_2)
        self.tweet=self.create_tweet(self.user_1)
        self.comment = self.create_comment(self.tweet.id,self.user_2.id)

    def test_unread_count(self):

        response = self.client_1.post(testconstants.NOTIFICATION_UNREAD_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client_1.get(testconstants.NOTIFICATION_UNREAD_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'],0)

    def test_mark_all_as_unread(self):
        self.assertEqual(self.client_1.get(testconstants.NOTIFICATION_UNREAD_URL).data['unread_count'], 0)
        data = {
            'tweet_id': self.tweet.id,
            'content': "test content"
        }
        self.client_2.post(testconstants.COMMENT_CREATE_API, data=data)
        self.assertEqual(self.client_1.get(testconstants.NOTIFICATION_UNREAD_URL).data['unread_count'], 1)
        response = self.client_1.get(testconstants.NOTIFICATION_MARK_READ_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client_1.get(testconstants.NOTIFICATION_UNREAD_URL).data['unread_count'], 1)
        response = self.client_1.post(testconstants.NOTIFICATION_MARK_READ_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client_1.get(testconstants.NOTIFICATION_UNREAD_URL).data['unread_count'], 0)

    def test_update_api_notifications(self):
        data = {
            'tweet_id': self.tweet.id,
            'content': "test content"
        }
        self.client_2.post(testconstants.COMMENT_CREATE_API, data=data)
        self.assertEqual(self.client_1.get(testconstants.NOTIFICATION_UNREAD_URL).data['unread_count'], 1)
        notification = self.user_1.notifications.first()

        data = {
            "id": notification.id,
            "unread": False
        }
        response = self.client_1.post(testconstants.NOTIFICATION_UPDATE_URL.format(notification.id), data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.anonymous_client.put(testconstants.NOTIFICATION_UPDATE_URL.format(notification.id), data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #try to update someone else's notification
        response = self.client_2.put(testconstants.NOTIFICATION_UPDATE_URL.format(notification.id), data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client_1.put(testconstants.NOTIFICATION_UPDATE_URL.format(notification.id), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread'], False)

        data['unread'] = True
        response = self.client_1.put(testconstants.NOTIFICATION_UPDATE_URL.format(notification.id), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread'], True)

        #no unreead
        del data['unread']

        response = self.client_1.put(testconstants.NOTIFICATION_UPDATE_URL.format(notification.id), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_comments_api_notifications(self):

        num_notifications = Notification.objects.all().count()
        self.assertEqual(num_notifications,0)
        data = {
            'tweet_id': self.tweet.id,
            'content': 'test content'
        }
        response = self.client_2.post(testconstants.COMMENT_CREATE_API, data=data)
        self.assertEqual(Notification.objects.all().count(), num_notifications+1)
        self.assertEqual(Comment.objects.all().count(), 2)

        #bad request should not send out notifications
        data['content'] = 'a'*280
        response = self.client_2.post(testconstants.COMMENT_CREATE_API, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Notification.objects.all().count(), num_notifications+1)
        self.assertEqual(Comment.objects.all().count(), 2)

    def test_likes_api_notifications(self):

        num_notifications = Notification.objects.all().count()
        num_likes = Like.objects.all().count()
        #tweet like notification
        data = {
            "content_type": "tweet",
            "object_id": self.tweet.id
        }
        response = self.client_2.post(testconstants.LIKE_CREATE_API, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.all().count(), num_notifications+1)
        self.assertEqual(Like.objects.all().count(), num_likes+1)
        data = {
            "content_type": "comment",
            "object_id": self.comment.id
        }

        #comment like notification
        response = self.client_1.post(testconstants.LIKE_CREATE_API, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.all().count(), num_likes+2)
        self.assertEqual(Notification.objects.all().count(), num_notifications+2)
        data['content_type']  = "testtype"
        response = self.client_2.post(testconstants.LIKE_CREATE_API, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Notification.objects.all().count(), num_notifications+2)
        self.assertEqual(Like.objects.all().count(), num_likes+2)
