from rest_framework.status import *
from likes.models import Like
from testing.testcases import TestCase
from testing.testconstants import *


class LikeApiTests(TestCase):

    #initial setup
    def setUp(self):
        self.users = [
            self.create_user(username="testuser{}".format(i))
            for i in range(3)
        ]
        self.clients = [
            self.login_user(self.users[i])
            for i in range(3)
        ]
        self.tweet=self.create_tweet(user=self.users[0])
        self.comment=self.create_comment(user_id=self.users[1].id,tweet_id=self.tweet.id)

    def test_create_like_api(self):

        #anonymous create
        data = {"content_type": "tweet", "object_id": self.tweet.id}
        response = self.anonymous_client.post(LIKE_CREATE_API,data=data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        #bad id
        data['object_id'] = -1
        response = self.clients[0].post(LIKE_CREATE_API, data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.all().count(), 0)

        #bad id
        data['object_id'] = self.tweet.id
        data['content_type'] = "test"
        response = self.clients[0].post(LIKE_CREATE_API, data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.all().count(),0)

        #like tweet
        data['content_type'] = 'tweet'
        response = self.clients[1].post(LIKE_CREATE_API, data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Like.objects.all().count(),1)

        #like tweet again
        response = self.clients[1].post(LIKE_CREATE_API, data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Like.objects.all().count(),1)

        #like comment
        data['content_type'] = 'comment'
        data['object_id'] = self.comment.id
        response = self.clients[0].post(LIKE_CREATE_API, data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Like.objects.all().count(), 2)

    def test_cancel_like_api(self):

        tweet_like = self.create_like(self.tweet, user=self.users[1])
        comment_like = self.create_like(self.comment, user=self.users[0])

        data = {"content_type": "tweet"}

        #no object_id
        response = self.clients[1].post(LIKE_CANCEL_API,data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.all().count(), 2)

        # no content_type
        data = {"object_id": 1}
        response = self.clients[1].post(LIKE_CANCEL_API, data=data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.all().count(), 2)

        #cancel with no like
        data = {"content_type": "tweet", "object_id": self.tweet.id}
        response = self.clients[2].post(LIKE_CANCEL_API, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Like.objects.all().count(), 2)

        #cancel tweet like
        data = {"content_type": "tweet", "object_id": self.tweet.id}
        response = self.clients[1].post(LIKE_CANCEL_API, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Like.objects.all().count(), 1)

        #cancel comment like
        data = {"content_type": "comment", "object_id": self.comment.id}
        response = self.clients[0].post(LIKE_CANCEL_API, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Like.objects.all().count(), 0)
