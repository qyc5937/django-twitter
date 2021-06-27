from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient
from inboxes.services import NotificationService
from comments.models import Comment
from likes.models import Like
from testing.testconstants import *
from tweets.models import Tweet
from newsfeeds.models import NewsFeed
from django.contrib.contenttypes.models import ContentType


class TestCase(DjangoTestCase):

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = TEST_PASSWORD
        if email is None:
            email = f'{username}@{TEST_DOMAIN}'
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet'
        return Tweet.objects.create(user=user, content=content)

    #only allow creating comment on tweets for now
    def create_comment(self, tweet_id, user_id, content=None):
        if content is None:
            content = "default comment"
        comment = Comment.objects.create(tweet_id=tweet_id, user_id=user_id, content=content)
        return comment

    def create_like(self, target, user):
        like = Like.objects.create(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return like

    def create_newsfeed(self, user, tweet):
        newsfeed = NewsFeed.objects.create(
            user = user,
            tweet = tweet,
        )
        return newsfeed

    def login_user(self, username, password=None):
        if password is None:
            password = TEST_PASSWORD
        #login first
        client = APIClient()
        client.post(LOGIN_URL, {
            'username': username,
            'password': password,
        })
        return client

    def get_num_followers(self, client, user):
        return len(client.get(FRIENDSHIP_FOLLOWERS_API.format(user.id)).data['results'])

    def get_num_followings(self, client, user):
        return len(client.get(FRIENDSHIP_FOLLOWINGS_API.format(user.id)).data['results'])

    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client
