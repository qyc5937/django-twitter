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
        self.tweets = [
            self.create_tweet(user=self.users[i%2], content="test tweet {}".format(i))
            for i in range(5)
        ]

    def test_destroy_api(self):

        comment = self.create_comment(user_id=self.users[1].id, tweet_id=self.tweets[0].id)
        #test anonymous login
        response = self.anonymous_client.delete(COMMENT_DESTROY_API.format(comment.id))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        #test deleting other's comments
        response = self.clients[0].delete(COMMENT_DESTROY_API.format(comment.id))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        #test deleting
        response = self.clients[1].delete(COMMENT_DESTROY_API.format(comment.id))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Comment.objects.filter(id=comment.id).exists(), False)

    def test_update_api(self):
        comment = self.create_comment(user_id=self.users[1].id, tweet_id=self.tweets[0].id)
        data = {"content": "test comment update"}

        #test anonymous login
        response = self.anonymous_client.put(COMMENT_UPDATE_API.format(comment.id), data=data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        #test update other's comment
        response = self.clients[0].put(COMMENT_UPDATE_API.format(comment.id), data=data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        #test update invalid comment id
        response = self.clients[0].put(COMMENT_UPDATE_API.format(-1), data=data)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

        #update without data
        response = self.clients[1].put(COMMENT_UPDATE_API.format(comment.id))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, data['content'])

        #UPDATE
        create_at, update_at = comment.created_at, comment.updated_at
        response = self.clients[1].put(COMMENT_UPDATE_API.format(comment.id), data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, data['content'])
        self.assertEqual(comment.user_id, self.users[1].id)
        self.assertEqual(comment.created_at, create_at)
        self.assertGreater(comment.updated_at, update_at)


    def test_create_api(self):

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
