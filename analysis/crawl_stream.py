"""
Twitter Stream Collector
Emerson Matson

Collects tweets from the Twitter sample stream.
"""

import tweepy

from prettylog import PrettyLog

from twitter import db

from twitter.models import Tweet

from analysis.connection import API

LOGGING = PrettyLog()


class TweetStreamListener(tweepy.StreamListener):
    """Configures the Stream Listener for storage"""
    num_tweets = 0

    # TODO(Consider using PrettyLog for this.)
    def on_connect(self):
        LOGGING.push("Successfully connected to Twitter streaming API.")

    def on_status(self, status):
        if (
            db.session.query(Tweet).filter_by(
                tweet_id=status.id
            ).count() == 0 and
            # TODO(Need to encode this into unicode.)
            len(str(status.text.encode('unicode_escape'))) < 1000
        ):
            LOGGING.push(
                "*" + status.user.name + "*: " + LOGGING.clean(status.text)
            )

            Tweet.store_tweet(status)

            self.num_tweets += 1

            if self.num_tweets % 100 == 0:
                LOGGING.push(
                    "*" + str(self.num_tweets) +
                    "* tweets have been collected."
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
