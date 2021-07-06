from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from friendships.services import FriendshipService
from utils.redis_helper import RedisHelper
from twitter.cache import USER_NEWSFEEDS_PATTERN
import logging

class NewsFeedService(object):

    '''
    Fan out a tweet onto the newfeeds timelines of all followers
    '''
    @classmethod
    def fan_out_to_followers(cls, tweet):
        followers = FriendshipService.get_followers(tweet.user)
        newsfeeds = [NewsFeed(tweet=tweet,user=follower,created_at=tweet.created_at) for follower in followers]
        #should be able to see own posts
        newsfeeds.append(NewsFeed(tweet=tweet,user=tweet.user,created_at=tweet.created_at))
        NewsFeed.objects.bulk_create(newsfeeds)

    '''
    Get up to date on tweets when a new friendship is created
    '''
    @classmethod
    def populate_newsfeed_for_friendship(cls, friendship):
#        logging.error(friendship)
        from_user, to_user = friendship.from_user, friendship.to_user
        newsfeeds = [
            NewsFeed(tweet=tweet, user=from_user,created_at=tweet.created_at)
            for tweet in Tweet.objects.filter(user=to_user)
        ]
        #create newsfeed in reverse order
        newsfeeds = newsfeeds[::-1]
        NewsFeed.objects.bulk_create(newsfeeds)

        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

    '''
    Remove tweets from timeline when a friendship has ended
    '''
    @classmethod
    def update_newsfeed_for_unfollow(cls,friendship):
 #       logging.error(friendship.from_user_id)
        from_user, to_user = friendship.from_user_id, friendship.to_user_id
        tweets = Tweet.objects.filter(user_id=to_user)
        NewsFeed.objects.filter(user_id=from_user,tweet__user__tweet__in=tweets).delete()

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id)
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key,queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        return RedisHelper.push_objects(key, newsfeed, queryset)
