from testing.testcases import TestCase
from notifications.models import Notification
from inboxes.services import NotificationService
# Create your tests here.
class InboxTest(TestCase):

    def setUp(self):
        self.user_1=self.create_user("user1")
        self.user_2=self.create_user("user2")
        self.tweet=self.create_tweet(self.user_1)
        self.comment = self.create_comment(self.tweet.id,self.user_2.id)

    def test_send_comments_service(self):

        num_notifications = Notification.objects.all().count()
        self.assertEqual(num_notifications,0)
        NotificationService.send_comment_notification(self.comment)
        self.assertEqual(Notification.objects.all().count(),num_notifications+1)

    def test_send_likes_service(self):

        num_notifications = Notification.objects.all().count()
        comment_like = self.create_like(self.comment,self.user_1)
        self.assertEqual(Notification.objects.all().count(), num_notifications)
        NotificationService.send_like_notificaion(comment_like)
        self.assertEqual(Notification.objects.all().count(), num_notifications+1)
        tweet_like = self.create_like(self.tweet,self.user_2)
        self.assertEqual(Notification.objects.all().count(), num_notifications+1)
        NotificationService.send_like_notificaion(tweet_like )
        self.assertEqual(Notification.objects.all().count(), num_notifications+2)
