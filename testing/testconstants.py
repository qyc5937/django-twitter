#common constants
TEST_USER='user1'
TEST_PASSWORD='testpassword'
TEST_EMAIL='testemail@test.com'
TEST_DOMAIN='test.com'
TEST_CONTENT='test content'
INVALID_USER_ID=9999

#account api URL
LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
SIGNUP_URL = '/api/accounts/signup/'

#tweet api URL
TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'

#friendship api URL
FRIENDSHIP_FOLLOWINGS_API = '/api/friendships/{}/followings/'
FRIENDSHIP_FOLLOWERS_API = '/api/friendships/{}/followers/'
FRIENDSHIP_FOLLOW_API = '/api/friendships/{}/follow/'
FRIENDSHIP_UNFOLLOW_API = '/api/friendships/{}/unfollow/'

#newsfeed api URL
NEWSFEED_LIST_API = '/api/newsfeeds/'