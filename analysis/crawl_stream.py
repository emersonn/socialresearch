"""
Twitter Stream Collector
Emerson Matson

Collects tweets from the Twitter sample stream.
"""

from colorama import Fore

import tweepy

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


class TweetStreamListener(tweepy.StreamListener):
    """Adds functionality to the Tweepy Stream Listener"""

    # TODO(Consider using PrettyLog for this.)
    def on_connect(self):
        print("Successfully connected to Twitter streaming API.")

    def on_status(self, status):
        print(
            Fore.GREEN + status.user.name + ": " +
            Fore.BLUE + status.text + Fore.RESET
        )

        # Checks for coordinates and places outside coordinates
        try:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]
        except TypeError:
            longitude = None
            latitude = None

        # Checks for the place otherwise it is undefined
        try:
            place = status.place.full_name
        except (TypeError, AttributeError):
            place = "Undefined"

        # TODO(Add try/except for very long tweets.)
        try:
            store_tweet = Tweet(
                text=str(status.text.encode('unicode_escape')),
                user_id=int(status.user.id_str),
                number=int(status.id_str),
                created_at=status.created_at,
                favorite_count=status.favorite_count,
                retweet_count=status.retweet_count,
                screen_name=status.user.screen_name,
                longitude=longitude,
                latitude=latitude,
                place=place
            )

            db.session.add(store_tweet)
            db.session.commit()
        except UnicodeDecodeError:
            print("Problem storing a unicode...")

    def on_error(self, status_code):
        if status_code == 420:
            print("Received 420. KKona.")
        else:
            print(
                "Received error with status code: ", str(status_code) +
                ". Disconnecting..."
            )
        return False

    def on_timeout(self):
        print("Server timed out...")
        return True

if __name__ == '__main__':
    stream_listener = TweetStreamListener()
    stream = tweepy.Stream(auth=API.auth, listener=stream_listener)

    print("Starting to collect the sample stream.")

    while 1:
        print(Fore.RED + "Starting Twitter stream..." + Fore.RESET)
        stream.sample()
