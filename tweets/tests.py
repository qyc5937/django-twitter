from django.test import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from datetime import datetime, timedelta

# Create your tests here.
class TweetTests(TestCase):

    def test_hours_to_now(self):
        test_user = User.objects.create_user(username='testuser')
        tweet= Tweet.objects.create(user=test_user,content='test tweet')
        tweet.created_at = datetime.utcnow() - timedelta(hours=1)
        tweet.save()
        self.assertEqual(tweet.hours_to_now,1)