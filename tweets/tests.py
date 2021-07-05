from datetime import datetime, timedelta

from django.contrib.auth.models import User
from tweets.services import TweetService
from twitter.cache import USER_TWEET_PATTERN
from likes.models import Like
from testing.testcases import TestCase
from tweets.models import Tweet,TweetPhoto
from tweets.constants import TweetPhotoStatus
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer

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

    def test_cache_tweet_in_redis(self):
        tweet = self.tweets[0]
        conn = RedisClient.get_connection()
        serialized_data = DjangoModelSerializer.serialize(tweet)
        conn.set(f'tweet:{tweet.id}', serialized_data)
        data=conn.get('tweet:bogus')
        self.assertEqual(data, None)

        data = conn.get(f'tweet:{tweet.id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(cached_tweet, tweet)

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


class TweetServiceTest(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')

    def test_get_user_tweets(self):
        tweet_ids = []
        for i in range(5):
            tweet = self.create_tweet(self.user1, 'test tweet{}'.format(i))
            tweet_ids.append(tweet.id)
        tweet_ids = tweet_ids[::-1]

        RedisClient.clear()
        conn = RedisClient.get_connection()

        #cache miss
        tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([tweet.id for tweet in tweets], tweet_ids)

        #cache hit
        tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([tweet.id for tweet in tweets], tweet_ids)

        #update
        new_tweet = self.create_tweet(self.user1, 'another tweet')
        tweets = TweetService.get_cached_tweets(self.user1.id)
        tweet_ids.insert(0, new_tweet.id)
        self.assertEqual([tweet.id for tweet in tweets], tweet_ids)

    def test_create_new_tweet_before_get_cached_tweets(self):
        tweet1 = self.create_tweet(self.user1, 'test tweet')
        RedisClient.clear()
        conn = RedisClient.get_connection()
        key = USER_TWEET_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(conn.exists(key), False)
        tweet2 = self.create_tweet(self.user1, 'another tweet')
        self.assertEqual(conn.exists(key), True)

        tweets = TweetService.get_cached_tweets(self.user1)
        self.assertEqual([tweet.id for tweet in tweets], [tweet2.id, tweet1.id])