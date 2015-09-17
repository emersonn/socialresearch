# Analyzes all the tweets in the database for words, tags, and classifications

import datetime

from colorama import Fore
from nltk.tokenize import WhitespaceTokenizer
from textblob.classifiers import NaiveBayesClassifier

from config import PRESET_TAGS, QUERY_LIMIT
from ..database import db_session
from models import Tweet, Word, Tag

COUNTER = 0

# TODO: Abstract this and accomodate for more classifications


def generate_classifier():
    print(Fore.GREEN + "Generating classifier..." + Fore.RESET)

    # Finds all tweets with classifications
    response_pos = (
        db_session.query(Tweet)
        .filter_by(**{"sentiment" + "_classify": "pos"})
        .all()
    )

    response_neg = (
        db_session.query(Tweet)
        .filter_by(**{"sentiment" + "_classify": "neg"})
        .all()
    )

    # Trains the classifier
    train_pos = [(response.text, "pos") for response in response_pos]
    train_neg = [(response.text, "neg") for response in response_neg]
    train = train_pos + train_neg

    cl = NaiveBayesClassifier(train)

    cl.show_informative_features(10)

    return cl

CL = generate_classifier()


def analyze_tweet(tweet):
    tweet.analyzed_date = datetime.datetime.now()
    db_session.add(tweet)
    db_session.commit()

    print("Analyzing tweet by " + str(tweet.user_id) + ".")

    # Tokenizes the words based on whitespace
    print("Analyzing words...")
    words = WhitespaceTokenizer().tokenize(tweet.text)
    for current_word in words:
        model = db_session.query(Word).filter_by(word=current_word).first()
        if not model:
            print(current_word + " does not exist. Creating...")
            model = Word(word=current_word)
            db_session.add(model)

        model.context.append(tweet)

        db_session.add(model)

    # TODO: slow processing. improve w/ backwards search.
    print("Analyzing tags...")
    for tag in PRESET_TAGS.keys():
        model = db_session.query(Tag).filter_by(tag=tag).first()
        if not model:
            print(tag + " does not exist. Creating...")
            model = Tag(tag=tag)
            db_session.add(model)

        print("Analyzing tag: " + tag + ".")
        for word in words:
            for classifier in PRESET_TAGS[tag]:
                if word == classifier:
                    print("Found tag" + tag + ". Adding and breaking...")
                    tweet.tags.append(model)
                    break

    # Analyzes the tweet's sentiment given the classifier
    sentiment = float(CL.prob_classify(tweet.text).prob("pos"))
    print("Setting sentiment to " + str(sentiment))
    tweet.sentiment_dist = sentiment

    db_session.add(tweet)
    db_session.commit()

    print("Finished analyzing tweet...")

if __name__ == "__main__":
    print("Welcome to the analysis script. Grabbing first query...")

    query = (
        db_session.query(Tweet)
        .filter_by(analyzed_date=None)
        .order_by(Tweet.created_at.desc())
        .limit(QUERY_LIMIT)
        .all()
    )

    while len(query) != 0:
        for tweet in query:
            COUNTER += 1
            print("On tweet number " + str(COUNTER) + ".")
            # Second check to allow for multiple scripts to run
            if not tweet.analyzed_date:
                analyze_tweet(tweet)

        print("Grabbing new query...")
        query = (
            db_session.query(Tweet)
            .filter_by(analyzed_date=None)
            .limit(QUERY_LIMIT)
            .all()
        )
