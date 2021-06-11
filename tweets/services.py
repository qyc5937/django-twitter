from tweets.models import TweetPhoto

class TweetService(object):
    @classmethod
    def create_tweet_photos(self, tweet, files):
        photos = []
        for order, file in enumerate(files):
            photo = TweetPhoto(
                user = tweet.user,
                tweet = tweet,
                file = file,
                order = order,
            )
            photos.append(photo)
        TweetPhoto.objects.bulk_create(photos)
