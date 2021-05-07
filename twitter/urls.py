from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from accounts.api import views
from tweets.api.views import TweetViewSet

router = routers.DefaultRouter()
router.register(r'api/users', views.UserViewSet)
router.register(r'api/accounts', views.AccountViewSet, basename='accounts')
router.register(r'api/tweets', TweetViewSet, basename='tweets')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')
         ),
]
