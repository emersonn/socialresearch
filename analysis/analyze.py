"""
Analysis Script
Emerson Matson

Analyzes the Tweets in the database by a number of features for data
representation.
"""

from random import shuffle

from string import punctuation

from nltk.classify.scikitlearn import SklearnClassifier

from nltk.corpus import stopwords

from nltk.stem.snowball import SnowballStemmer

from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize

from sklearn.metrics import classification_report
from sklearn.svm import LinearSVC

from progressbar import ProgressBar

from prettylog import PrettyLog

from twitter import db

from twitter.models import Tweet

# TODO(Improve this search for stop words.)
STOPWORDS = set(stopwords.words('english') + list(punctuation))

CATEGORIES = [
    'Christianity',
    'Islam'
]

LOGGING = PrettyLog()


def remove_stopwords(text):
    result = []
    for word in text:
        if word not in STOPWORDS:
            result.append(word)

    return result


def stem_text(text):
    result = []

    stemmer = SnowballStemmer("english")
    for word in text:
        result.append(stemmer.stem(word))

    return result


def clean_text(text):
    return stem_text(
        remove_stopwords(
            text
        )
    )


def get_classify_set():
    """Returns the classified training set from the database.

    Returns:
        List of tuples: (cleaned text, classification)
    """

    results = []

    # TODO(This is the easy way to train the set. Find another way.)
    #   Crawling websites and finding words that relate to it so it can
    #       search those instead or use those as features.
    for category in CATEGORIES:
        tweets = (
            db.session.query(Tweet).filter(Tweet.text.contains(category)).all()
        )

        if tweets:
            clean_add(tweets, results, category)
        else:
            print("No tweets were found for #" + category + "#.")

    return results


def assign_features(text):
    features = {}
    for word in text:
        features['contains({text})'.format(text=word.lower())] = True

    return features


def clean_add(tweets, results, label):
    progress = ProgressBar()

    for tweet in progress(tweets):
        sentences = sent_tokenize(tweet.text)
        tokenized = []

        for sentence in sentences:
            tokenized.extend(word_tokenize(sentence.lower()))

        results.append((
            assign_features(clean_text(tokenized)),
            label
        ))


def classify_tweets():
    """Combines Scikit-Learn and NLTK with a SVM to classify tweets."""

    # For easy training, can just search all tweets with the key word Islam
    #   And train the set from there. Stemming and eliminating stop words.
    classified = get_classify_set()

    # Train the set.
    shuffle(classified)
    test_size = int(len(classified) * .1)

    train_set = classified[test_size:]
    test_set = classified[:test_size]

    print("Training set is: " + str(train_set))
    print("Test set is: " + str(test_set))

    # TODO(Use a SVC instead of a LinearSVC for probabilities.)
    classifier = SklearnClassifier(LinearSVC())
    classifier.train(train_set)

    # TODO(Make this into a neater lambda function.)
    test_features, test_label = [], []
    for item in test_set:
        test_features.append(item[0])
        test_label.append(item[1])

    classified_test = classifier.batch_classify(test_features)
    print(classification_report(
        test_label, classified_test,
        labels=list(set(test_label)),
        target_names=CATEGORIES
    ))

if __name__ == "__main__":
    LOGGING.push("Starting to *classify* tweets.")
    classify_tweets()
    LOGGING.push("Finished *classifying* tweets.")
