from testing.testcases import TestCase
from testing.testconstants import *
from rest_framework.status import *
from comments.models import Comment
import logging
class CommentApiTests(TestCase):

    #initial setup
    def setUp(self):
        self.users = [
            self.create_user(username="testuser{}".format(i))
            for i in range(2)
        ]
        self.clients = [
            self.login_user(self.users[i])
            for i in range(2)
        ]
        #post tweet
        for i in range(5):
            self.create_tweet(user=self.users[i%2], content="test tweet {}".format(i))

    def test_comments(self):

        data={
            "tweet_id": 1,
        }

        #no login list
        response = self.anonymous_client.get(COMMENT_LIST_API,data=data)
        self.assertEqual(response.status_code,HTTP_200_OK)
        self.assertEqual(len(response.data),2)


        #post content too short
        data['content'] = 'ab'
        response = self.clients[0].post(COMMENT_CREATE_API, data=data)
        self.assertEqual(response.status_code,HTTP_400_BAD_REQUEST)

        #post content too long
        data['content'] = '18asdf'*140,
        response = self.clients[0].post(COMMENT_CREATE_API, data=data)
        self.assertEqual(response.status_code,HTTP_400_BAD_REQUEST)
        #comment on own tweet
        comment_count = Comment.objects.count()
        data['tweet_id'] = 1
        data['content'] ='test content'
        response = self.clients[0].post(COMMENT_CREATE_API, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), comment_count+1)
        comment_count+=1
        #comment on someone else's tweet
        data['tweet_id'] = 2
        response = self.clients[0].post(COMMENT_CREATE_API, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), comment_count+1)
        #no login create comment
        response = self.anonymous_client.post(COMMENT_CREATE_API, data=data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        #list comments for tweet
        response = self.clients[0].get(COMMENT_LIST_API, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 1)

