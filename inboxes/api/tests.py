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
        self.user_1=self.create_user("user1")
        self.user_2=self.create_user("user2")
        self.client_1 = self.login_user(self.user_1)
        self.client_2 = self.login_user(self.user_2)
        self.tweet=self.create_tweet(self.user_1)
        self.comment = self.create_comment(self.tweet.id,self.user_2.id)

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
        print(Notification.objects.all())
        self.assertEqual(Like.objects.all().count(), num_likes+2)
        self.assertEqual(Notification.objects.all().count(), num_notifications+2)
        data['content_type']  = "testtype"
        response = self.client_2.post(testconstants.LIKE_CREATE_API, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Notification.objects.all().count(), num_notifications+2)
        self.assertEqual(Like.objects.all().count(), num_likes+2)
