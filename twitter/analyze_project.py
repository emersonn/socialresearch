import random

import nltk
from nltk.tokenize import word_tokenize
from textblob.classifiers import NaiveBayesClassifier

from colorama import Fore

from ..database import db_session

import models

LOCATIONS = ('Berlin, Germany', 'Seattle, WA', 'Los Angeles, CA')

# God is sometimes used colloquially and not in a religious context
CHRISTIAN_KEYWORDS = ('God', 'Bible', 'Jesus', 'Jesus Christ', 'Church')
MUSLIM_KEYWORDS = ('Koran', "Quran", "Q'uran", "Allah", "Mosque")

def generate_classifier():
    print(Fore.GREEN + "Generating classifier..." + Fore.RESET)

    # TODO: make this more general rather than having "sentiment"
    response_pos = db_session.query(models.Tweet).filter_by(**{"sentiment" + "_classify": "pos"}).all()
    response_neg = db_session.query(models.Tweet).filter_by(**{"sentiment" + "_classify": "neg"}).all()

    train_pos = [(response.text, "pos") for response in response_pos]
    train_neg = [(response.text, "neg") for response in response_neg]
    train = train_pos + train_neg

    cl = NaiveBayesClassifier(train)

    cl.show_informative_features(10)

    return cl

CL = generate_classifier()

def analyze_topic(tweets, place, topic, num_tweets):
    print(Fore.MAGENTA + "There are " + str(len(tweets)) + " " + topic + " tweets in " + place + "." + Fore.RESET)
    print(Fore.CYAN + "This constitutes " + str(round(len(tweets) * 1.0 / models.Tweet.query.filter_by(place = place).count() * 100)) + "% of " + place + " tweets." + Fore.RESET)

    print(Fore.RED + "Here are some samples." + Fore.RESET)
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

    classifications = 0.0
    for tweet in tweets:
        classifications += CL.prob_classify(tweet.text).prob("pos")

    print(Fore.YELLOW + place + " has a sentiment of " + str(classifications / len(tweets)) + " towards " + topic + "." + Fore.RESET)

        # print(response.text)
        # print(cl.classify(response.text) + " " + str(cl.prob_classify(response.text).prob("pos")))


def analyze_keywords(keywords, tag, num_tweets):
    tweets = {}

    for place in LOCATIONS:
        tweets[place] = set()
        for keyword in keywords:
            query = models.Tweet.query.filter_by(place = place).filter(models.Tweet.text.like("%" + keyword + "%")).all()
            for tweet in query:
                tweets[place].add(tweet)

        analyze_topic(tweets[place], place, tag, num_tweets)

    return tweets

# TODO: occurances of each religion, sentiment towards each religion, similar words in each
# religion
def analyze_religion(num_tweets):
    christian_tweets = analyze_keywords(CHRISTIAN_KEYWORDS, "Christian", num_tweets)
    muslim_tweets = analyze_keywords(MUSLIM_KEYWORDS, "Muslim", num_tweets)

if __name__ == "__main__":
    num_tweets = models.Tweet.query.count()
    print(Fore.GREEN + "There are " + str(num_tweets) + " tweets in the database." + Fore.RESET)

    analyze_religion(num_tweets)
