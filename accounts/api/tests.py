import shutil

from testing.testcases import TestCase
from testing.testconstants import *
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import UserProfile

class UserProfileApiTest(TestCase):

    def test_update_profile(self):
        user_1 = self.create_user(TEST_USER)
        user_2 = self.create_user('another')
        client_1 = self.login_user(TEST_USER)
        client_2 = self.login_user(user_2)
        profile = user_1.profile
        profile.nickname = 'one nickname'
        profile.save()
        url = PROFILE_UPDATE_URL.format(profile.id)
        response = self.anonymous_client.put(url, {
            'nickname': 'two nickname'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        profile.refresh_from_db()
        self.assertEqual(profile.nickname, 'one nickname')
        response = client_2.put(url, {
            'nickname': 'two nickname'
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        profile.refresh_from_db()
        self.assertEqual(profile.nickname, 'one nickname')

        # update nickname
        response = client_1.put(url, {
            'nickname': 'two nickname'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertEqual(profile.nickname, 'two nickname')

        #update avatar
        response = client_1.put(url, {
            'avatar': SimpleUploadedFile(
                name='avatar.jpg',
                content=str.encode('test'),
                content_type='image/jpeg',
            ),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('avatar' in response.data['avatar'], True)
        profile.refresh_from_db()
        self.assertIsNotNone(profile.avatar)


class AccountApiTests(TestCase):

    #initial setup
    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(
            username=TEST_USER,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
        )

    #test login functionality
    def test_login(self):
        wrong_user='wronguser'
        wrong_pass='wksadjkfasf'

        #Using GET method to auth
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': TEST_PASSWORD
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        #invalid login
        response = self.client.post(LOGIN_URL, {
            'username': wrong_user,
            'password': wrong_pass,
        })
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

        #not logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        #proper login


        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': TEST_PASSWORD,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['user'], None)
        self.assertNotEqual(response.data['user']['id'], None)
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(response.data['user']['id'], self.user.id)

        #test login status

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):

        #login first
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': TEST_PASSWORD,
        })
        #test logout
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)
        response = self.client.post(LOGOUT_URL, None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #test that login status reflects the logout
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'],False)

    def test_signup(self):

        num_profiles = UserProfile.objects.all().count()

        data ={
            'password': TEST_PASSWORD,
            'email': TEST_EMAIL
        }


        #no username
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #get request
        response = self.client.get(SIGNUP_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        #short username
        data['username'] = 'a'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #long username
        data['username'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #bad email
        data['username'] = TEST_USER
        data['email'] = 'aa'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #short password
        data['email'] = TEST_EMAIL
        data['password'] = 'aa'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #long password
        data['password'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #proper registration
        data = {'username': 'newuser',
                'email': 'newuser@tes.com',
                'password': 'testpass',}
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'newuser')

        # make sure that user profile is created
        self.assertEqual(UserProfile.objects.all().count(), num_profiles+1)
        user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user_id=user_id).first()
        self.assertNotEqual(profile, None)
        #test user is logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
