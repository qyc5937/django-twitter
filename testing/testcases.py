from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from testing.testconstants import *
from tweets.models import Tweet
from comments.models import Comment
from rest_framework.test import APIClient

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
        return Comment.objects.create(tweet_id=tweet_id, user_id=user_id, content=content)

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
        return len(client.get(FRIENDSHIP_FOLLOWERS_API.format(user.id)).data)

    def get_num_followings(self, client, user):
        return len(client.get(FRIENDSHIP_FOLLOWINGS_API.format(user.id)).data)

    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client
