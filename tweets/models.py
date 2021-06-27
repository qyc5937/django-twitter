from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from accounts.services import UserService
from likes.models import Like



class Tweet(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="who post the this tweet",
    )

    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        # time zones should all be utc
        return (datetime.utcnow() - self.created_at).seconds // 3600

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return UserService.get_user_through_cache(self.user_id)

class TweetPhoto(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField()
    order = models.IntegerField(default=0)

    #photo status
    status = models.IntegerField(
        default = TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at',),
            ('is_deleted', 'created_at',),
            ('status', 'created_at',),
            ('tweet', 'order',),
        )

    def __str__(self):
        return f'{self.tweet.id}: {self.file}'
