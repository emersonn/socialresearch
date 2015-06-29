import random

import nltk
from nltk.tokenize import word_tokenize
from colorama import Fore

from ..database import db_session

import models

LOCATIONS = ('Berlin, Germany', 'Seattle, WA', 'Los Angeles, CA')

# God is sometimes used colloquially and not in a religious context
CHRISTIAN_KEYWORDS = ('God', 'Bible', 'Jesus', 'Jesus Christ', 'Church')
MUSLIM_KEYWORDS = ('Koran', "Quran", "Q'uran", "Allah", "Mosque")

def analyze_topic(tweets, place, topic):
    print(Fore.BLUE + "There are " + str(len(tweets)) + " " + topic + " tweets in " + place + "." + Fore.RESET)

    print("Here are some samples.")
    for tweet in random.sample(tweets, min(10, len(tweets))):
        print(tweet.text)

    word_list = []

    for tweet in tweets:
        word_list.extend(word_tokenize(tweet.text))

    freq_dist = nltk.FreqDist(word_list)
    common_words = [word for word in freq_dist.most_common(49) if len(word[0]) > 2]

    print(Fore.BLUE + "Here are the most popular words related to " + topic + " and in " + place + "." + Fore.RESET)
    print(common_words)

    # TODO: needs NLTK.download()
    # text = nltk.Text(word_list)
    # print text.collocations()

    # Analyze sentiment here and also get the important words in the positive and negative

def analyze_keywords(keywords, tag):
    tweets = {}

    for place in LOCATIONS:
        tweets[place] = set()
        for keyword in keywords:
            query = models.Tweet.query.filter_by(place = place).filter(models.Tweet.text.like("%" + keyword + "%")).all()
            for tweet in query:
                tweets[place].add(tweet)

        analyze_topic(tweets[place], place, tag)

    return tweets

# TODO: occurances of each religion, sentiment towards each religion, similar words in each
# religion
def analyze_religion(num_tweets):
    christian_tweets = analyze_keywords(CHRISTIAN_KEYWORDS, "Christian")
    muslim_tweets = analyze_keywords(MUSLIM_KEYWORDS, "Muslim")

if __name__ == "__main__":
    num_tweets = models.Tweet.query.count()
    print(Fore.GREEN + "There are " + str(num_tweets) + " tweets in the database." + Fore.RESET)

    analyze_religion(num_tweets)
