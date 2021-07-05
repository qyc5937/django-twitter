from tweets.models import TweetPhoto, Tweet
from utils.redis_helper import RedisHelper
from twitter.cache import USER_TWEET_PATTERN


class TweetService(object):

    @classmethod
    def create_tweet_photos(self, tweet, files):
        photos = []
        for order, file in enumerate(files):
            photo = TweetPhoto(
                user = tweet.user,
                tweet = tweet,
                file = file,
                order = order,
            )
            photos.append(photo)
        TweetPhoto.objects.bulk_create(photos)

    @classmethod
    def get_cached_tweets(cls, user_id):
        queryset =  Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_TWEET_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_tweets_to_cache(cls, tweet):
        queryset = Tweet.objects.filter(user=tweet.user).order_by('-created_at')
        key = USER_TWEET_PATTERN.format(user_id=tweet.user_id)
        RedisHelper.push_objects(key, tweet, queryset)
