import nltk
from nltk.tokenize import word_tokenize
import random

from ..database import db_session

import models

LOCATIONS = ('Berlin, Germany', 'Seattle, WA')

# God is sometimes used colloquially and not in a religious context
CHRISTIAN_KEYWORDS = ('God', 'Bible', 'Jesus', 'Jesus Christ', 'Church')
MUSLIM_KEYWORDS = ('Koran', "Quran", "Q'uran", "Allah", "Mosque")

def analyze_topic(tweets, place, topic):
    print("There are " + str(len(tweets)) + " " + topic + " tweets in " + place + ".")

    print("Here are some samples.")
    for tweet in random.sample(tweets, min(10, len(tweets))):
        print(tweet.text)

    word_list = []

    for tweet in tweets:
        word_list.extend(word_tokenize(tweet.text))

    freq_dist = nltk.FreqDist(word_list)
    common_words = [word for word in freq_dist.most_common(49) if len(word[0]) > 2]

    print("Here are the most popular words related to " + topic + " and in " + place + ".")
    print(common_words)

    # TODO: needs NLTK.download()
    # text = nltk.Text(word_list)
    # print text.collocations()

    # Analyze sentiment here and also get the important words in the positive and negative

# TODO: occurances of each religion, sentiment towards each religion, similar words in each
# religion
def analyze_religion(num_tweets):

    # Christian
    christian_tweets = {}
    for place in LOCATIONS:
        christian_tweets[place] = set()
        for keyword in CHRISTIAN_KEYWORDS:
            query = models.Tweet.query.filter_by(place = place).filter(models.Tweet.text.like("%" + keyword + "%")).all()
            for tweet in query:
                christian_tweets[place].add(tweet)

        analyze_topic(christian_tweets[place], place, "Christian")

    # Muslim
    muslim_tweets = {}

    # TODO: put this into a different method
    for place in LOCATIONS:
        muslim_tweets[place] = set()
        for keyword in MUSLIM_KEYWORDS:
            query = models.Tweet.query.filter_by(place = place).filter(models.Tweet.text.like("%" + keyword + "%")).all()
            for tweet in query:
                muslim_tweets[place].add(tweet)

        analyze_topic(muslim_tweets[place], place, "Muslim")





if __name__ == "__main__":
    num_tweets = models.Tweet.query.count()
    print("There are " + str(num_tweets) + " tweets in the database.")

    analyze_religion(num_tweets)
