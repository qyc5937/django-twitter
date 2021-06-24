from testing.testcases import TestCase
from testing.testconstants import *
from rest_framework.test import APIClient
from friendships.models import Friendship
from utils.constants import MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE
from rest_framework.status import *
import logging


class FriendshipApiTests(TestCase):

    def setUp(self):
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
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['user']['username'], self.user3.username)

        # test zero followings

        response = self.anonymous_client.get(FRIENDSHIP_FOLLOWINGS_API.format(self.user2.id))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_followers_api(self):
        # get followers
        response = self.anonymous_client.get(FRIENDSHIP_FOLLOWERS_API.format(self.user3.id))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(self.get_num_followers(self.anonymous_client, self.user3), 1)
        self.assertEqual(response.data['results'][0]['user']['username'], self.user1.username)

        # zero followers
        response = self.anonymous_client.get(FRIENDSHIP_FOLLOWERS_API.format(self.user4.id))
        self.assertEqual(len(response.data['results']), 0)

    def test_follower_pagination(self):
        max_page_size = MAX_PAGE_SIZE
        page_size =  DEFAULT_PAGE_SIZE
        for i in range(page_size *2):
            follower = self.create_user('test_user_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user1)
            if follower.id %2 == 0:
                Friendship.objects.create(from_user=self.user2, to_user=follower)

        url = FRIENDSHIP_FOLLOWERS_API.format(self.user1.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        #has not followed anyone
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        response = self.user2_client.get(url, {'page': 1})
        for result in response.data['results']:
            if result['user']['id'] %2 != 0:
                self.assertEqual(result['has_followed'], False)
            else:
                self.assertEqual(result['has_followed'], True)

    def test_following_pagination(self):
        max_page_size = MAX_PAGE_SIZE
        page_size =  DEFAULT_PAGE_SIZE
        #adjust folloinwg numbers to share boilerplate code
        num_followings = self.get_num_followings(self.user1_client, self.user1)
        for i in range(page_size *2 - num_followings ):
            following = self.create_user('test_user_following{}'.format(i))
            Friendship.objects.create(from_user=self.user1, to_user=following)
            if following.id %2 == 0:
                Friendship.objects.create(from_user=self.user2, to_user=following)

        url = FRIENDSHIP_FOLLOWINGS_API.format(self.user1.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        #has not followed anyone
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        response = self.user2_client.get(url, {'page': 1})
        for result in response.data['results']:
            if result['user']['id'] %2 != 0:
                self.assertEqual(result['has_followed'], False)
            else:
                self.assertEqual(result['has_followed'], True)

        #user 1 should have followed all followings
        response = self.user1_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

    def _test_friendship_pagination(self, url, page_size, max_page_size):
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size*2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_pages'], True)

        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['has_next_pages'], False)

        response = self.anonymous_client.get(url, {'page': 3})
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

        #test that page size cannot exceed max page size
        response = self.anonymous_client.get(url, {'page': 1, 'size': max_page_size+1})
        self.assertEqual(len(response.data['results']), max_page_size)

        #test that page size can be customized

        response = self.anonymous_client.get(url, {'page': 1, 'size': 1})
        self.assertEqual(len(response.data['results']), 1)

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
        #print(self.user1_client.get(FRIENDSHIP_FOLLOWERS_API.format(self.user1.id)).data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(self.get_num_followers(self.user1_client, self.user4), num_followers + 1)

        # dupe follow
        response = self.user1_client.post(FRIENDSHIP_FOLLOW_API.format(self.user4.id))
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['duplicate'], True)

        # follow invalid user
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
