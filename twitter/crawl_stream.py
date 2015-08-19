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
# United States vs Germany
"""
LOCATIONS = (('berlin', (13.09, 52.34, 13.76, 52.68)),
             ('seattle', (-122.44, 47.50, -122.24, 47.73)),
             ('los_angeles', (-118.67, 33.70, -118.16, 34.34)),
             ('new_york', (-74, 40, -73, 41)),
             ('hanover', (9.61, 52.31, 9.92, 52.45)),
             ('jena', (11.54, 50.88, 11.63, 50.97)),
             ('frankfurt', (8.47, 50.02, 8.79, 50.23)),
             ('stuttgart', (9.03, 48.68, 9.31, 48.86)))
"""

# General
LOCATIONS = (
    ('united_kingdom', (-13.41393, 49.16209, 1.76896, 60.854691)),
    ('united_states', (-179.150558, 18.91172, -66.940643, 71.441048)),
    ('germany', (5.86624, 47.27021, 15.04205, 55.05814)),
    ('egypt', (24.698099, 22, 36.89468, 31.674179)),
    ('south_africa', (16.46841, -46.990009, 37.993172, -22.12472)),
    ('china', (73.557701, 15.77539, 134.773605, 53.5606)),
    ('australia', (112.921112, -54.640301, 159.278717, -9.22882)),
    ('mexico', (-118.867172, 14.53285, -86.703392, 32.71862)),
    ('canada', (-141.002701, 41.681019, -52.620201, 83.110619)),
    ('france', (-5.1406, 41.33374, 9.55932, 51.089062)),
    ('russia', (-168.997849, 41.185902, 19.638861, 81.856903)),
    ('italy', (6.62665, 35.49308, 18.520281, 47.091999)),
)

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
            # print(Fore.GREEN + status.user.name + ": " + Fore.BLUE + status.text.encode('ascii', 'ignore').decode('ascii') + Fore.RESET)
            print("Got tweet: " + str(status.id_str) + ".")

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
                screen_name = status.user.screen_name,
                longitude = longitude,
                latitude = latitude,
                place = place)

            db_session.add(store_tweet)
            db_session.commit()
        except UnicodeDecodeError:
            print("Problem storing a unicode...")

    def on_error(self, status_code):
        if status_code == 420:
            print("Received 420 (blaze it). Disconnecting...")
        else:
            print("Received error with status code: ", str(status_code) + ". Disconnecting...")
        return False

    def on_timeout(self):
        print("Server timed out...")
        return True

if __name__ == '__main__':
    stream_listener = TweetStreamListener()
    stream = tweepy.Stream(auth = API.auth, listener = stream_listener)

    # Depricated location filtering, using sample now
    """
    locations = []
    for location in LOCATIONS:
        for point in location[1]:
            locations.append(point)

    print("Filtering the stream with locations: " + str(locations))
    """

    print("Using sample stream...")

    # stream.filter(locations = [13.09, 52.34, 13.76, 52.68, -122.44, 47.50, -122.24, 47.73])
    # TODO: Very hacky. Make it so it doesn't use a while loop and try, except. Also include in logging.
    import sqlalchemy
    while 1:
        try:
            print(Fore.RED + "Starting Twitter stream..." + Fore.RESET)
            # stream.filter(locations = locations)
            stream.sample()
        except UnicodeDecodeError:
            pass
        except sqlalchemy.exc.DataError:
            pass

    # stream.filter(track=['penis'])
