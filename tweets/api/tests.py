from testing.testcases import TestCase
from testing.testconstants import *
from rest_framework.test import APIClient
from tweets.models import Tweet
import sys

class TweetApiTests(TestCase):

    def setUp(self):
        #anonymous login client
        self.anonymous_client = APIClient()
        self.user1 = self.create_user(TEST_USER, TEST_EMAIL)
        self.user2 = self.create_user('user2')
        self.user1_tweets = [
            self.create_tweet(self.user1)
            for i in range(6)
        ]
        #create auth login client
        self.auth_client = self.login_user(TEST_USER, TEST_PASSWORD)
        self.user2_tweets = [
            self.create_tweet(self.user2)
            for i in range(4)
        ]

    def test_list_api(self):
        #test anonymous user
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        #normal request
        response = self.anonymous_client.get(TWEET_LIST_API,{
            'user_id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 6)

        response = self.anonymous_client.get(TWEET_LIST_API, {
            'user_id': self.user2.id
        })
        self.assertEqual(len(response.data['tweets']),4)

        #test ordering
        self.assertEqual(response.data['tweets'][0]['id'], self.user2_tweets[-1].id)
        self.assertEqual(response.data['tweets'][-1]['id'], self.user2_tweets[0].id)

    def test_create_api(self):
        data= {'content': 'test content'}
        # no login
        response = self.anonymous_client.post(TWEET_CREATE_API, data)
        self.assertEqual(response.status_code, 403)

        # no content
        response = self.auth_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)
        #content too short
        data['content'] ='1'
        response = self.auth_client.post(TWEET_CREATE_API,data)
        self.assertEqual(response.status_code, 400)
        #content too long
        data['content'] ='asdkfjasdkfjaklsdfjlkasdjfl;kasdj;flajs;ldkfjkas;ldfjlkasdjf;laskjdfljasdlfjaskldfj;lasjdflaskjdf;lfkjasdlkfjlasdjfkl;asdjf;lkasdj;flajsdkl;fjakls;dfj;lasdjf;lkasjd;flkjasd;klfja;slkdfj;lkasdjf;klasdjf;lkasj;flkasjdfkasdjfklasdjf;lkasdjflkasdjfklasdjfklajsdlkfjsakldfjasdlkfjsadlkfjaslkdjfsldak;jlf1'
        response = self.auth_client.post(TWEET_CREATE_API,data)
        self.assertEqual(response.status_code, 400)
        #normal post
        tweet_count = Tweet.objects.count()
        data['content'] = TEST_CONTENT
        response = self.auth_client.post(TWEET_CREATE_API, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(),tweet_count+1)