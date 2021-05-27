from comments.models import Comment
from tweets.models import Tweet
from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify
from django.contrib.auth.models import User


class NotificationService(object):

    @classmethod
    def send_like_notificaion(cls, like):
        target = like.content_object
        if like.user == target.user:
            return
        if like.content_type == ContentType.objects.get_for_model(Tweet):
            sender = User.objects.get(username=like.user)
            recipient = User.objects.get(username=target.user)
            notify.send(
                sender=sender,
                recipient=recipient,
                verb='liked your tweet',
                target=target,
            )
        if like.content_type == ContentType.objects.get_for_model(Comment):
            sender = User.objects.get(username=like.user)
            recipient = User.objects.get(username=target.user)
            notify.send(
                sender=sender,
                recipient=recipient,
                verb='liked your comment',
                target=target,
            )

    @classmethod
    def send_comment_notification(cls, comment):
        if comment.user == comment.tweet.user:
            return
        notify.send(
            comment.user,
            recipient=comment.tweet.user,
            verb='commented on your tweet',
            target=comment.tweet
        )
