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
TWEET_RETRIEVE_API = '/api/tweets/{}/'
TWEET_CREATE_API = '/api/tweets/'

#friendship api URL
FRIENDSHIP_FOLLOWINGS_API = '/api/friendships/{}/followings/'
FRIENDSHIP_FOLLOWERS_API = '/api/friendships/{}/followers/'
FRIENDSHIP_FOLLOW_API = '/api/friendships/{}/follow/'
FRIENDSHIP_UNFOLLOW_API = '/api/friendships/{}/unfollow/'

#newsfeed api URL
NEWSFEED_LIST_API = '/api/newsfeeds/'

#comments api URL
COMMENT_LIST_API = '/api/comments/'
COMMENT_CREATE_API = '/api/comments/'
COMMENT_DESTROY_API = '/api/comments/{}/'
COMMENT_UPDATE_API = '/api/comments/{}/'

#like api URL
LIKE_CREATE_API = '/api/likes/'
LIKE_CANCEL_API = '/api/likes/cancel/'

#notification api URL
NOTIFICATION_UNREAD_URL= '/api/notifications/unread-count/'
NOTIFICATION_MARK_READ_URL = '/api/notifications/mark-all-as-read/'
NOTIFICATION_UPDATE_URL= '/api/notifications/{}/'
