from testing.testcases import TestCase
from testing.testconstants import *
from rest_framework.test import APIClient
from friendships.models import Friendship
from rest_framework.status import *
import logging


class FriendshipApiTests(TestCase):

    def setUp(self):
        # anonymous login client
        self.anonymous_client = APIClient()
        self.user1 = self.create_user(TEST_USER, TEST_EMAIL)
        self.user2 = self.create_user('user2')
        self.user3 = self.create_user('user3')
        self.user4 = self.create_user('user4')
        # create auth login client
        self.user1_client = self.login_user(self.user1.username, TEST_PASSWORD)
        self.user2_client = self.login_user(self.user2.username, TEST_PASSWORD)
        self.user3_client = self.login_user(self.user3.username, TEST_PASSWORD)
        self.user4_client = self.login_user(self.user4.username, TEST_PASSWORD)
        Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        Friendship.objects.create(from_user=self.user1, to_user=self.user3)
        Friendship.objects.create(from_user=self.user3, to_user=self.user2)

    def test_followings_api(self):
        # get followings
        response = self.anonymous_client.get(FRIENDSHIP_FOLLOWINGS_API.format(self.user1.id))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['followings']), 2)
        self.assertEqual(response.data['followings'][0]['user']['username'], self.user3.username)

        # test zero followings

        response = self.anonymous_client.get(FRIENDSHIP_FOLLOWINGS_API.format(self.user2.id))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['followings']), 0)

    def test_followers_api(self):
        # get followers
        response = self.anonymous_client.get(FRIENDSHIP_FOLLOWERS_API.format(self.user3.id))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(self.get_num_followers(self.anonymous_client, self.user3), 1)
        self.assertEqual(response.data[0]['user']['username'], self.user1.username)

        # zero followers
        response = self.anonymous_client.get(FRIENDSHIP_FOLLOWERS_API.format(self.user4.id))
        self.assertEqual(len(response.data), 0)

    def test_follow_api(self):
        # anonymous follow
        response = self.anonymous_client.post(FRIENDSHIP_FOLLOW_API.format(self.user1.id))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        # follow self
        response = self.user1_client.post(FRIENDSHIP_FOLLOW_API.format(self.user1.id))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # following using get
        response = self.user1_client.get(FRIENDSHIP_FOLLOW_API.format(self.user3.id))
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)
        # success follow
        num_followers = self.get_num_followers(self.user1_client, self.user4)
        response = self.user1_client.post(FRIENDSHIP_FOLLOW_API.format(self.user4.id))
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(self.get_num_followers(self.user1_client, self.user4), num_followers + 1)

        # dupe follow
        response = self.user1_client.post(FRIENDSHIP_FOLLOW_API.format(self.user4.id))
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['duplicate'], True)

        # follow invalid usesre
        response = self.user1_client.post(FRIENDSHIP_FOLLOW_API.format(INVALID_USER_ID))
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

        #reverse follow
        friendships_count = Friendship.objects.all().count()
        response = self.user3_client.post(FRIENDSHIP_FOLLOW_API.format(self.user1.id))
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.all().count(), friendships_count+1)

    def test_unfollow_api(self):
        response = self.anonymous_client.post(FRIENDSHIP_UNFOLLOW_API.format(self.user1.id))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        # unfollow self
        response = self.user1_client.post(FRIENDSHIP_UNFOLLOW_API.format(self.user1.id))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # success unfollow
        num_followers = self.get_num_followers(self.user1_client, self.user3)
        response = self.user1_client.post(FRIENDSHIP_UNFOLLOW_API.format(self.user3.id))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(self.get_num_followers(self.user1_client, self.user3), num_followers - 1)

        # unfollow none existing friendship
        num_followers = self.get_num_followers(self.user1_client, self.user3)
        response = self.user1_client.post(FRIENDSHIP_UNFOLLOW_API.format(self.user3.id))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['deleted'],0)

        # unfollow invalid usesre
        response = self.user1_client.post(FRIENDSHIP_UNFOLLOW_API.format(INVALID_USER_ID))
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)




'''    def test_list_api(self):
        #test anonymous user
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        #normal request
        response = self.anonymous_client.get(TWEET_LIST_API,{
            'user_id': self.user1.id
        })
        self.assertEqual(response.status_code, HTTP_200_OK)
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
'''
