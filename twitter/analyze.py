# Analyzes all the tweets in the database for words, tags, and classifications

import datetime

from colorama import Fore
from nltk.tokenize import WhitespaceTokenizer
from textblob.classifiers import NaiveBayesClassifier

from config import DEBUG, PRESET_TAGS, QUERY_LIMIT
from ..database import db_session
from models import Tweet, Word, Tag


def generate_classifier():
    desired = raw_input("What classification is the focus on? ")

    print(Fore.GREEN + "Generating classifier..." + Fore.RESET)

    # Finds all tweets with classifications
    response_pos = (
        db_session.query(Tweet)
        .filter_by(**{desired + "_classify": "pos"})
        .all()
    )

    response_neg = (
        db_session.query(Tweet)
        .filter_by(**{desired + "_classify": "neg"})
        .all()
    )

    train_pos = [(response.text, "pos") for response in response_pos]
    train_neg = [(response.text, "neg") for response in response_neg]
    train = train_pos + train_neg

    cl = NaiveBayesClassifier(train)
    if DEBUG:
        cl.show_informative_features(10)
    return cl


def analyze_tweet(tweet, classifier):
    # Update the tweet right away to ensure simultaneous configuration
    tweet.analyzed_date = datetime.datetime.now()
    db_session.commit()

    print("Analyzing tweet by " + str(tweet.user_id) + ".")

    # Tokenizes the words based on whitespace
    # TODO: Get another solution to word analysis.
    words = WhitespaceTokenizer().tokenize(tweet.text)
    for current_word in words:
        model = db_session.query(Word).filter_by(word=current_word).first()
        if not model:
            print(current_word + " does not exist. Creating.")
            model = Word(word=current_word)
            db_session.add(model)
        model.context.append(tweet)

    for tag in PRESET_TAGS.keys():
        model = db_session.query(Tag).filter_by(tag=tag).first()
        if not model:
            print(tag + " does not exist in the database. Creating.")
            model = Tag(tag=tag)
            db_session.add(model)

        print("Analyzing tag: " + tag + ".")
        if any(curr in tweet.text for curr in PRESET_TAGS[tag]):
            print("Found tag: " + tag + ". Adding to tweet.")
            tweet.tags.append(model)

    # Analyzes the tweet's sentiment given the classifier
    sentiment = float(classifier.prob_classify(tweet.text).prob("pos"))
    print("Setting sentiment to: " + str(sentiment) + ".")
    tweet.sentiment_dist = sentiment

    db_session.commit()
    print("Finished analyzing tweet.")


def analyze_database():
    classifier = generate_classifier()
    counter = 0

    print("Grabbing first query.")
    query = grab_needed_tweets()

    while query:
        for tweet in query:
            counter += 1
            print("On tweet (count): " + str(counter) + ".")

            # Second check to allow for silmultaneity
            if not tweet.analyzed_date:
                analyze_tweet(tweet, classifier)

        print("Grabbing new query...")
        query = grab_needed_tweets()


def grab_needed_tweets():
    return (
        db_session.query(Tweet)
        .filter_by(analyzed_date=None)
        .order_by(Tweet.created_at.desc())
        .limit(QUERY_LIMIT)
        .all()
    )


if __name__ == "__main__":
    if DEBUG:
        print("Debug mode is ON.")

    print("Welcome to the analysis script.")

    analyze_database()
