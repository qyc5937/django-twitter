from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import sys

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
SIGNUP_URL = '/api/accounts/signup/'
TEST_USERNAME= 'testuser'
TEST_PASSWORD= 'testpass'
TEST_EMAIL='testemail@test.com'

class AccountApiTests(TestCase):

    #initial setup
    def setUp(self):
        self.client = APIClient()
        self.user = self.createUser(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
        )

    #create user
    def createUser(self, username, email, password):
        return User.objects.create_user(username=username, password=password, email=email)

    #test login functionality
    def test_login(self):
        wrong_user='wronguser'
        wrong_pass='wksadjkfasf'

        #Using GET method to auth
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': TEST_PASSWORD
        })
        self.assertEqual(response.status_code, 405)

        #invalid login
        response = self.client.post(LOGIN_URL, {
            'username': wrong_user,
            'password': wrong_pass,
        })
        self.assertEqual(response.status_code,400)

        #not logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        #proper login


        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': TEST_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertNotEqual(response.data['user']['email'], None)
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(response.data['user']['email'], TEST_EMAIL)

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
        self.assertEqual(response.status_code, 200)

        #test that login status reflects the logout
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'],False)

    def test_signup(self):

        data ={
            'password': TEST_PASSWORD,
            'email': TEST_EMAIL
        }


        #no username
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 400)

        #get request
        response = self.client.get(SIGNUP_URL)
        self.assertEqual(response.status_code, 405)

        #short username
        data['username'] = 'a'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 400)

        #long username
        data['username'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 400)

        #bad email
        data['username'] = TEST_USERNAME
        data['email'] = 'aa'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 400)

        #short password
        data['email'] = TEST_EMAIL
        data['password'] = 'aa'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 400)

        #long password
        data['password'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 400)

        #proper registration
        data = {'username': 'newuser',
                'email': 'newuser@tes.com',
                'password': 'testpass',}
        print(data, file=sys.stderr)
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'newuser')

        #test user is logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, 200)
