from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

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
