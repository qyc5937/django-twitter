from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from testing.testconstants import *
from tweets.models import Tweet
from rest_framework.test import APIClient

class TestCase(DjangoTestCase):

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = TEST_PASSWORD
        if email is None:
            email = f'{username}@{TEST_DOMAIN}'
        return User.objects.create_user(username, email, password)

    def create_tweet(self, username, content=None):
        if content is None:
            content = 'default tweet'
        return Tweet.objects.create(user=username, content=content)

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