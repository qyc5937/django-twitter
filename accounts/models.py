from django.db import models
from django.contrib.auth.models import User
from accounts.listeners import user_changed, profile_changed
from django.db.models.signals import post_save, pre_delete

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    avatar = models.FileField(null=True)
    nickname = models.CharField(max_length=140, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return 'user: {} - nickname: {}'.format(self.user, self.nickname)


def get_profile(user):
    #avoid cyclical dependency
    from accounts.services import UserService
    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile = UserService.get_profile_through_cache(user.id)
    setattr(user, '_cached_user_profile', profile)
    return profile


User.profile = property(get_profile)

#use listener to invalidate cache when user/profile changes
pre_delete.connect(user_changed, sender=User)
pre_delete.connect(profile_changed, sender=UserProfile)

post_save.connect(user_changed, sender=User)
post_save.connect(profile_changed, sender=UserProfile)
