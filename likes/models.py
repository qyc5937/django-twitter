from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Like(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        on_delete=models.SET_NULL,
    )
    object_id = models.PositiveIntegerField()
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('content_type', 'object_id', 'created_at'))
        unique_together = (('content_type', 'object_id', 'user',))
        ordering = (('content_type', 'object_id', '-created_at',))

    def __str__(self):
        return '{} - {} liked {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )