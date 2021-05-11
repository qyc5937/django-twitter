from testing.testcases import TestCase
from testing.testconstants import *
from rest_framework.test import APIClient
from rest_framework.status import *
import logging
class NewsFeedApiTests(TestCase):
#    reset_sequences = True
    #initial setup
    def setUp(self):
        self.users = [
            self.create_user(username='{}_{}'.format(TEST_USER,i))
            for i in range(3)
        ]
        self.clients = [
            self.login_user(self.users[i].username, TEST_PASSWORD)
            for i in range(3)
        ]
        self.tweets = [
            self.clients[0].post(TWEET_CREATE_API,{'content': 'testing_{}'.format(i)})
            for i in range(3)
        ]
        self.tweets+=[
            self.clients[1].post(TWEET_CREATE_API, {'content': 'testing_{}'.format(i)})
            for i in range(5,7)
        ]

    def test_newsfeed(self):

        #no login
        response = self.anonymous_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        #see own tweets
        response = self.clients[0].get(NEWSFEED_LIST_API)
        self.assertEqual(len(response.data['newsfeed']),3)
        self.assertEqual(response.data['newsfeed'][0]['tweet']['content'],'testing_2')
        #post
        response = self.clients[0].post(NEWSFEED_LIST_API,{'test': 'testing'})
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)
        #no newsfeed
        response = self.clients[2].get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeed']),0)

        #following gets
        self.clients[1].post(FRIENDSHIP_FOLLOW_API.format(self.users[0].id))
        self.clients[2].post(FRIENDSHIP_FOLLOW_API.format(self.users[0].id))
        response = self.clients[2].post(FRIENDSHIP_FOLLOW_API.format(self.users[1].id))
        response = self.clients[2].get(NEWSFEED_LIST_API)
        #test accounts
        self.assertEqual(len(response.data['newsfeed']),5)
        #test ordering of tweets
        self.assertEqual(response.data['newsfeed'][0]['tweet']['content'],'testing_6')

        response = self.clients[1].get(NEWSFEED_LIST_API)
        self.assertEqual(len(response.data['newsfeed']),5)

        #post and confirm that newsfeeds is updated
        test_content= 'newsfeed test'

        self.clients[0].post(TWEET_CREATE_API,{'content': test_content})
        response = self.clients[2].get(NEWSFEED_LIST_API)
        self.assertEqual(response.data['newsfeed'][0]['tweet']['content'], test_content)
        response = self.clients[1].get(NEWSFEED_LIST_API)
        self.assertEqual(response.data['newsfeed'][0]['tweet']['content'], test_content)


        #unfollow
        self.clients[2].post(FRIENDSHIP_UNFOLLOW_API.format(self.users[0].id))
        response = self.clients[2].get(NEWSFEED_LIST_API)
        self.assertEqual(len(response.data['newsfeed']),2)
        self.assertEqual(response.data['newsfeed'][0]['tweet']['content'], 'testing_6')

        #post another tweet and confirm newsfeed is only deliver the the one remaining follower
        test_content= 'newsfeed test2'
        self.clients[0].post(TWEET_CREATE_API,{'content': test_content})
        response = self.clients[2].get(NEWSFEED_LIST_API)
        self.assertEqual(response.data['newsfeed'][0]['tweet']['content'], 'testing_6')
        response = self.clients[1].get(NEWSFEED_LIST_API)
        self.assertEqual(response.data['newsfeed'][0]['tweet']['content'], test_content)
