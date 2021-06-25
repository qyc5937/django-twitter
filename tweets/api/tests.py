from testing.testcases import TestCase
from tweets.constants import TWEET_PHOTO_MAX_NUM
from testing.testconstants import *
from tweets.models import Tweet, TweetPhoto
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from comments.models import Comment
from utils.constants import *
from utils.paginations import EndlessPagination
import logging
class TweetApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user(TEST_USER, TEST_EMAIL)
        self.user2 = self.create_user('user2')
        self.user3 = self.create_user('user3')
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

    def test_tweet_list_api(self):
        #test anonymous user
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #normal request
        response = self.anonymous_client.get(TWEET_LIST_API,{
            'user_id': self.user1.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 6)

        response = self.anonymous_client.get(TWEET_LIST_API, {
            'user_id': self.user2.id
        })
        self.assertEqual(len(response.data['results']),4)

        #test ordering
        self.assertEqual(response.data['results'][0]['id'], self.user2_tweets[-1].id)
        self.assertEqual(response.data['results'][-1]['id'], self.user2_tweets[0].id)


    def test_tweet_likes(self):
        # test likes
        self.assertEqual(self.user1_tweets[0].like_set.count(), 0)
        self.create_like(self.user1_tweets[0], self.user2)
        self.assertEqual(self.user1_tweets[0].like_set.count(), 1)
        self.create_like(self.user1_tweets[0], self.user3)
        self.assertEqual(self.user1_tweets[0].like_set.count(), 2)

        # check likes in response data
        response = self.anonymous_client.get(TWEET_LIST_API, {
            'user_id': self.user1.id
        })

        self.assertEqual(len(response.data['results'][-1]['likes']), 2)
        comment = self.create_comment(tweet_id=self.user1_tweets[0].id,user_id=self.user2.id)
        self.comments = Comment.objects.all()
        # create likes on comment
        self.create_like(self.comments[0], self.user3)
        self.assertEqual(self.comments[0].like_set.count(), 1)
        response = self.auth_client.get(TWEET_RETRIEVE_API.format(self.user1_tweets[0].id), data={"with_all_comments": True})

        # check likes info in response data.
        self.assertEqual(len(response.data['likes']), 2)
        self.assertEqual(len(response.data['comments'][0]['likes']), 1)

    def test_tweet_create_api(self):
        data= {'content': 'test content'}
        # no login
        response = self.anonymous_client.post(TWEET_CREATE_API, data)
        self.assertEqual(response.status_code, 403)

        # no content
        response = self.auth_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #content too short
        data['content'] ='1'
        response = self.auth_client.post(TWEET_CREATE_API,data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #content too long
        data['content'] ='abcd' * 100
        response = self.auth_client.post(TWEET_CREATE_API,data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #normal post
        tweet_count = Tweet.objects.count()
        data['content'] = TEST_CONTENT
        response = self.auth_client.post(TWEET_CREATE_API, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(),tweet_count+1)

    def test_tweet_retrieve_api(self):
        test_tweet = self.user1_tweets[0]
        logging.error(TWEET_RETRIEVE_API.format(test_tweet.id))
        #retrieve with no comments
        response = self.auth_client.get(TWEET_RETRIEVE_API.format(test_tweet.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']),0)

        data = {'tweet_id': test_tweet.id}
        #create comments
        for i in range(12):
            data['content'] = 'comment # {} on tweet {}'.format(i, test_tweet.id)
            self.auth_client.post(COMMENT_CREATE_API, data=data)

        #get default comments
        response = self.auth_client.get(TWEET_RETRIEVE_API.format(test_tweet.id))
        self.assertEqual(len(response.data['comments']),DEFAULT_COMMENT_DISPLAY_NUM)
        #get all comments
        response = self.auth_client.get(TWEET_RETRIEVE_API.format(test_tweet.id), data={"with_all_comments": True})
        self.assertEqual(len(response.data['comments']),12)
        #get preview
        response = self.auth_client.get(TWEET_RETRIEVE_API.format(test_tweet.id), data={"with_preview_comments": True})
        self.assertEqual(len(response.data['comments']), PREVIEW_COMMENT_DISPLAY_NUM)

    def test_tweet_create_with_photos(self):

        def seek_files(files):
            for file in files:
                file.seek(0)

        data = {
            'content': 'a test tweet',
            'files': [],
        }
        # empty files
        response = self.auth_client.post(TWEET_CREATE_API, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        #:single photo
        files = [
            SimpleUploadedFile(
                name=f'selfie{i}.jpg',
                content=str.encode(f'selfie{i}'),
                content_type='image/jpg',
            )
            for i in range(10)
        ]
        '''data['files'] = [SimpleUploadedFile(
            name='testfile.jpg',
            content=str.encode('test file'),
            content_type='image/jpeg',
        )]'''
        data['files'] = [files[0]]
        seek_files(files)
        response = self.auth_client.post(TWEET_CREATE_API, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TweetPhoto.objects.count(), 1)

        #more than 9

        data['files'] = files
        seek_files(files)
        response = self.auth_client.post(TWEET_CREATE_API, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TweetPhoto.objects.count(), 1)
        files.pop()
        seek_files(files)
        data['files'] = files
        response = self.auth_client.post(TWEET_CREATE_API, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TweetPhoto.objects.count(), TWEET_PHOTO_MAX_NUM+1)

    def test_tweet_pagination(self):
        page_size = EndlessPagination.page_size

        for i in range(2*page_size - len(self.user1_tweets)):
            self.user1_tweets.append(self.create_tweet(self.user1, 'tweet {}'.format(i)))

        tweets = self.user1_tweets[::-1]
        #page 1
        response = self.auth_client.get(TWEET_LIST_API.format(self.user1.id), {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], tweets[0].id)
        self.assertEqual(response.data['results'][1]['id'], tweets[1].id)
        self.assertEqual(response.data['results'][page_size-1]['id'], tweets[page_size-1].id)

        #page 2
        response = self.auth_client.get(TWEET_LIST_API.format(self.user1.id), {
            'user_id': self.user1.id,
            'created_at__lt': tweets[page_size-1].created_at
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], tweets[page_size].id)
        self.assertEqual(response.data['results'][1]['id'], tweets[page_size+1].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], tweets[2*page_size - 1].id)


        #get latest tweets
        new_tweet = self.create_tweet(self.user1, "new tweet")
        response = self.auth_client.get(TWEET_LIST_API.format(self.user1.id), {
            'user_id': self.user1.id,
            'created_at__gt': tweets[0].created_at
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_tweet.id)



