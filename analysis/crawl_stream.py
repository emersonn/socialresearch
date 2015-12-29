"""
Twitter Stream Collector
Emerson Matson

Collects tweets from the Twitter sample stream.
"""

from sqlalchemy.exc import DataError

import tweepy

from prettylog import PrettyLog

# TODO(Consider separating both of these modules? Too interlinked?)
from twitter import app
from twitter import db

from twitter.models import Tweet

CONSUMER_KEY = app.config['CONSUMER_KEY']
CONSUMER_SECRET = app.config['CONSUMER_SECRET']
ACCESS_TOKEN = app.config['ACCESS_TOKEN']
ACCESS_SECRET = app.config['ACCESS_SECRET']

AUTH = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
AUTH.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
API = tweepy.API(AUTH)

LOGGING = PrettyLog()


class TweetStreamListener(tweepy.StreamListener):
    """Configures the Stream Listener for storage"""
    num_tweets = 0

    # TODO(Consider using PrettyLog for this.)
    def on_connect(self):
        LOGGING.push("Successfully connected to Twitter streaming API.")

    def on_status(self, status):
        LOGGING.push(
            "*" + status.user.name + "*: " + LOGGING.clean(status.text)
        )

        self.num_tweets += 1

        try:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]
        except TypeError:
            longitude = None
            latitude = None

        try:
            place = status.place.full_name
        except (TypeError, AttributeError):
            place = None

        try:
            store_tweet = Tweet(
                text=str(status.text.encode('unicode_escape')),

                user_id=int(status.user.id_str),
                screen_name=status.user.screen_name,

                number=int(status.id_str),
                created_at=status.created_at,

                favorite_count=status.favorite_count,
                retweet_count=status.retweet_count,

                longitude=longitude,
                latitude=latitude,
                place=place
            )

            db.session.add(store_tweet)
            db.session.commit()
        except DataError:
            LOGGING.push("Tweet too long, skipping.")

        if self.num_tweets % 100 == 0:
            LOGGING.push(
                "*" + str(self.num_tweets) + "* tweets have been collected."
            )

    def on_error(self, status_code):
        LOGGING.push(
            "Received error with status code: #", str(status_code) +
            "#. Disconnecting from stream."
        )

        return False

    def on_timeout(self):
        LOGGING.push("Server timed out.")

        return True

if __name__ == '__main__':
    stream_listener = TweetStreamListener()
    stream = tweepy.Stream(auth=API.auth, listener=stream_listener)

    LOGGING.push("Starting to collect the sample stream.")
    stream.sample()
