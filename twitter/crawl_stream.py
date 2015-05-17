import tweepy, datetime

from colorama import Fore

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

# http://isithackday.com/geoplanet-explorer/index.php?woeid=2345496
LOCATIONS = (('berlin', (13.09, 52.34, 13.76, 52.68)),
             ('seattle', (-122.44, 47.50, -122.24, 47.73)),
             ('los_angeles', (-118.67, 33.70, -118.16, 34.34)),
             ('new_york', (-74, 40, -73, 41)))

# TODO: find a good place for this? maybe this might belong somewhere else?
AUTH = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
AUTH.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
API = tweepy.API(AUTH)

class TweetStreamListener(tweepy.StreamListener):

    def on_connect(self):
        print("Successfully connected to Twitter streaming API...")

    def on_status(self, status):
        try:
            print(Fore.GREEN + status.user.name + ": " + Fore.BLUE + status.text + Fore.RESET)
        except UnicodeEncodeError:
            # TODO: fix this, very hacky workaround to run on server
            print(Fore.GREEN + status.user.name + ": " + Fore.BLUE + status.text.decode('ascii', 'ignore') + Fore.RESET)

        try:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]
        except TypeError:
            longitude = 200
            latitude = 100

        try:
            place = status.place.full_name
        except TypeError:
            place = "Undefined"
        except AttributeError:
            place = "Undefined"

        try:
            store_tweet = models.Tweet(text = str(status.text.encode('unicode_escape')),
                user_id = int(status.user.id_str),
                number = int(status.id_str),
                created_at = status.created_at,
                favorite_count = status.favorite_count,
                retweet_count = status.retweet_count,
                longitude = longitude,
                latitude = latitude,
                place = place)

            db_session.add(store_tweet)
            db_session.commit()
        except UnicodeDecodeError:
            print("Problem storing a unicode...")

    def on_error(self, status_code):
        if status_code == 420:
            print("Received 420. Disconnecting...")
            return False

if __name__ == '__main__':
    stream_listener = TweetStreamListener()
    stream = tweepy.Stream(auth = API.auth, listener = stream_listener)

    locations = []
    for location in LOCATIONS:
        for point in location[1]:
            locations.append(point)

    print("Filtering the stream with locations: " + str(locations))


    # stream.filter(locations = [13.09, 52.34, 13.76, 52.68, -122.44, 47.50, -122.24, 47.73])
    # TODO: Very hacky. Make it so it doesn't use a while loop and try, except. Also include in logging.
    import sqlalchemy
    while 1:
        try:
            print(Fore.RED + "Starting Twitter stream..." + Fore.RESET)
            stream.filter(locations = locations)
        except UnicodeDecodeError:
            pass
        except sqlalchemy.exc.DataError:
            pass

    # stream.filter(track=['penis'])
