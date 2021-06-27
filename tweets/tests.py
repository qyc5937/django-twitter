from datetime import datetime, timedelta

from django.contrib.auth.models import User

from likes.models import Like
from testing.testcases import TestCase
from tweets.models import Tweet,TweetPhoto
from tweets.constants import TweetPhotoStatus

# Create your tests here.
class TweetTests(TestCase):

    #initial setup
    def setUp(self):
        self.clear_cache()
        self.users = [
            self.create_user(username="testuser{}".format(i))
            for i in range(2)
        ]
        self.clients = [
            self.login_user(self.users[i])
            for i in range(2)
        ]
        #post tweet
        self.tweets = [
            self.create_tweet(user=self.users[i%2], content="test tweet {}".format(i))
            for i in range(5)
        ]

    def test_hours_to_now(self):
        test_user = User.objects.create_user(username='testuser')
        tweet = Tweet.objects.create(user=test_user, content='test tweet')
        tweet.created_at = datetime.utcnow() - timedelta(hours=1)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 1)

    def test_tweet_model(self):

        self.assertNotEqual(self.tweets[0].__str__(), None)

    def test_tweet_like_set(self):

        like_count = Like.objects.all().count()
        self.create_like(target=self.tweets[0], user=self.users[1])
        self.assertEqual(Like.objects.all().count(), like_count+1)
        self.assertEqual(self.tweets[0].like_set.count(),1)
        self.assertEqual(self.tweets[0].like_set[0].user_id, self.users[1].id)

    def test_create_tweet_photo(self):
        tweet_photo = TweetPhoto.objects.create(
            user = self.users[0],
            tweet = self.tweets[0],
        )
        self.assertEqual(tweet_photo.user.id, self.users[0].id)
        self.assertEqual(tweet_photo.tweet.id, self.tweets[0].id)
        self.assertEqual(tweet_photo.status, TweetPhotoStatus.PENDING)
