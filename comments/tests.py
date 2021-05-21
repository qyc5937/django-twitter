from testing.testcases import TestCase
from django.contrib.contenttypes.models import ContentType
from likes.models import Like

class CommentModelTests(TestCase):

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
        self.test_comment = self.create_comment(user_id=self.users[0].id,tweet_id=self.tweets[0].id, content='test comment')

    def test_comment_model(self):

        self.assertNotEqual(self.test_comment.__str__(), None)

    def test_comment_like_set(self):

        like_count = Like.objects.all().count()
        self.create_like(target=self.test_comment, user=self.users[1])
        self.assertEqual(Like.objects.all().count(), like_count+1)
        self.assertEqual(self.test_comment.like_set.count(),1)
        self.assertEqual(self.test_comment.like_set[0].user_id, self.users[1].id)


