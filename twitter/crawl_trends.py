import datetime, tweepy

from ..database import db_session

import models

# todo: fix this. there are warnings about python 2.7 and also
# SSL. maybe need to implement SSL because using HTTPS in the
# requests?
import logging
logging.captureWarnings(True)

CONSUMER_KEY = "Fyk4egy7QSrIqxX20lkl3a1WU"
CONSUMER_SECRET = "WCgiP6q2vnVu7uq4oIOcMVZhQmmV3RsH4lrqtNf6KjXUlsl5lU"

ACCESS_TOKEN = "1714296900-aVCQhI3HfjUnzDtGqWRZ7LvzGIad6bmWwB4HIIK"
ACCESS_SECRET = "Ez00jB4IDK3mQQqsVPjtROOQL95LzjsTuuqIRghwLClJB"

# TODO: make this more mutable? make it so it searches wherever the person wants
#       to search can search on the script call?
WOEID = (('berlin', 638242, 52.52, 13.38),
         ('seattle', 2490383, 47.6, -122.33),
         ('new_york', 2459115, 40.71, -74.01),
         ('los_angeles', 2442047, 34.05, -118.25))

DEFAULT_RADIUS = 10

# TODO: find a good place for this? maybe this might belong somewhere else?
AUTH = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
AUTH.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
API = tweepy.API(AUTH, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

def crawl_trends():
    print('Now crawling Twitter trends for: ' + ', '.join(place[0].replace('_', ' ') for place in WOEID) + "...")

    # TODO: implement overusage of the script so tweets and trends aren't duplicated in the dataset
    for place in WOEID:
        print("Now crawling Twitter trends specifically for: " + place[0] + " (" + str(place[1]) + ")...")

        trends = API.trends_place(place[1])[0]
        trends_date = trends['created_at']
        trends_list = [(trend['name'], trend['query']) for trend in trends['trends']]

        print("Found trends for " + place[0] + ". Consists of: " + ", ".join(trend[0] for trend in trends_list))
        print("Now searching tweets for this particular trend...")

        for trend in trends_list:
            print("Now storing trend: " + trend[0])
            trending = models.Trend(stored = datetime.datetime.strptime(trends_date, '%Y-%m-%dT%H:%M:%SZ'),
                query = trend[1],
                name = trend[0],
                place = place[0]
            )
            db_session.add(trending)

            tweets = API.search(trend[1], geocode = str(place[2]) + "," + str(place[3]) + "," + str(DEFAULT_RADIUS) + "mi")
            store_tweets(tweets, trending, place)

        db_session.commit()

def store_tweets(tweets, trend, place):
    print("Now storing tweets for a particular trend: " + trend.name)

    # tweet.text, tweet.id_str, tweet.favorite_count,
    # tweet.coordinates (nullable) (maybe just use the place instead? place passed in = None defualt),
    # tweet.retweet_count,
    # tweet.user.id_str?, maybe store the user data for later? description and stuff?
    # tweet.created_at, tweet.place.name? (lots of stuff)
    for tweet in tweets:
        print("Storing tweet: " + tweet.id_str)

        try:
            longitude = tweet.coordinates['coordinates'][0]
            latitude = tweet.coordinates['coordinates'][1]
        except TypeError:
            longitude = place[3]
            latitude = place[2]

        store_tweet = models.Tweet(text = str(tweet.text.encode('unicode_escape')),
            user_id = int(tweet.user.id_str),
            number = int(tweet.id_str),
            created_at = tweet.created_at,
            favorite_count = tweet.favorite_count,
            retweet_count = tweet.retweet_count,
            longitude = longitude,
            latitude = latitude,
            trend_id = trend.id,
            trend = trend,
            place = place[0])
        db_session.add(store_tweet)
    db_session.commit()

# TODO: implement crawling users' tweets
def crawl_users():
    pass


if __name__ == "__main__":
    crawl_trends()

    print("Finished crawling trends for all places listed...")
