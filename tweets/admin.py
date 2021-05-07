from django.contrib import admin
from tweets.models import Tweet
from datetime import datetime

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'created_at',
        'user',
        'content',
    )

