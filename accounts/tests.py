from testing.testcases import TestCase
from testing.testconstants import *
from accounts.models import UserProfile

class UserProfileTests(TestCase):

    #initial setup
    def test_profile_property(self):
        test_user = self.create_user(TEST_USER)
        self.assertEqual(UserProfile.objects.count(), 0)
        profile = test_user.profile
        self.assertEqual(isinstance(profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)
