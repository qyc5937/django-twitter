from testing.testcases import TestCase
from friendships.models import Friendship
from friendships.services import FriendshipService

# Create your tests here.
class FriendshipServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')

    def test_get_followings(self):
        user3 = self.create_user('user3')
        user4 = self.create_user('user4')
        for to_user in [self.user2,user3,user4]:
            Friendship.objects.create(to_user=to_user, from_user = self.user1)
        FriendshipService.invalidated_following_cache(self.user1.id)

        user_id_set = FriendshipService.get_following_user_id_set(self.user1.id)
        self.assertEqual(user_id_set, {self.user2.id, user3.id, user4.id})

        Friendship.objects.filter(to_user=self.user2, from_user=self.user1).delete()
        FriendshipService.invalidated_following_cache(self.user1.id)
        user_id_set = FriendshipService.get_following_user_id_set(self.user1.id)
        self.assertEqual(user_id_set, {user3.id, user4.id})
