"""
Search Crawler
Emerson Matson

Crawls the Twitter Search with a starting point topic and stores given
Tweets that match.
"""

import time

from sqlalchemy.exc import DataError

import tweepy

from prettylog import PrettyLog

from twitter.models import Tweet

from analysis.connection import AUTH

API = tweepy.API(AUTH, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# TODO(Abstract this out.)
CATEGORIES = [
    'Christian',
    'Muslim',
    'Buddhist',
    'None'
]

LOGGING = PrettyLog()


def limit_handled(cursor):
    """Limits the cursor's accesses with respect to the rate limit.

    Args:
        cursor: Cursor to limit.

    Notes:
        Once the rate limit is reached, program execution waits 15 minutes.
    """

    while True:
        """
        remaining = int(API.last_response.getheader('x-rate-limit-remaining'))
        if remaining == 0:
            # limit = int(API.last_response.getheader('x-rate-limit-limit'))

            reset = int(API.last_response.getheader('x-rate-limit-reset'))
            reset = datetime.fromtimestamp(reset)
            print('Rate limit reached until: {reset}'.format(reset=reset))

            delay = (reset - datetime.now()).total_seconds() + 12
            print('Sleeping for ' + str(delay) + ' seconds.')
            time.sleep(delay)
        """
        try:
            yield cursor.next()
        except tweepy.TweepError:
            LOGGING.push("Rate limit reached, waiting 15 minutes.")
            time.sleep(15 * 60)


def crawl_category(category):
    """Crawls a specific given category.

    Args:
        category: Category to search for.
    """
    cursor = limit_handled(
        tweepy.Cursor(API.search, q=category, count=100).items(1000)
    )

    for status in cursor:
        LOGGING.push(
            "*" + status.user.name + "*: " + LOGGING.clean(status.text)
        )

        try:
            Tweet.store_tweet(status)
        except DataError:
            LOGGING.push("Tweet too long, skipping.")


def crawl_search():
    """Crawls the search."""

    for category in CATEGORIES:
        crawl_category(category)

    # Stem out into related common words with searches?

if __name__ == "__main__":
    LOGGING.push("Starting to crawl the search.")
    crawl_search()
    LOGGING.push("Finished crawling the search.")
