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
# from sklearn.svm import LinearSVC
from sklearn.svm import SVC

from progressbar import Bar
from progressbar import ETA
from progressbar import Percentage
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


def remove_stopwords(text, stopwords=STOPWORDS):
    """Removes stopwords from a given list of words.

    Args:
        text: List of strings to filter.
        stopwords: Set of stop words to look for. Default is STOPWORDS.

    Returns:
        list of strings: Filtered text.
    """

    result = []
    for word in text:
        if word not in STOPWORDS:
            result.append(word)

    return result


def stem_text(text):
    """Stems the given (English) text.

    Args:
        text: List of strings to stem.

    Returns:
        list of strings: Stemmed text.
    """

    result = []

    stemmer = SnowballStemmer("english")
    for word in text:
        result.append(stemmer.stem(word))

    return result


def clean_text(text):
    """Cleans the given text by stemming it and removing stop words.

    Args:
        text: List of strings to clean.

    Returns:
        list of strings: Cleaned text.
    """

    return stem_text(
        remove_stopwords(
            text
        )
    )


def get_classify_set(categories=CATEGORIES):
    """Returns the classified training set from the database.

    Args:
        categories: List of categories to consider for classification.
            All of the categories are strings to match.

    Returns:
        List of tuples: (cleaned text, classification)
    """

    results = []

    # TODO(This is the easy way to train the set. Find another way.)
    #   Crawling websites and finding words that relate to it so it can
    #       search those instead or use those as features.

    # TODO(Does there need to be a None category? Would it help?)
    for category in CATEGORIES:
        LOGGING.push("Assigning category: @" + category + "@.")

        tweets = (
            db.session.query(Tweet).filter(Tweet.text.contains(category)).all()
        )

        if tweets:
            clean_add(tweets, results, category)
        else:
            LOGGING.push("No tweets were found for #" + category + "#.")

    return results


def assign_features(text):
    """Assigns features of the given text.

    Args:
        text: List of strings to assign features to.

    Returns:
        dictionary: Dictionary of strings to booleans.
            Strings in the format of features with booleans
            indicating existence.
    """

    features = {}
    for word in text:
        features['contains({text})'.format(text=word.lower())] = True

    return features


def tokenize_full(text):
    """Tokenizes a text by to words.

    Args:
        text: A string to tokenize.

    Returns:
        list of strings: A fully tokenized text.
    """

    sentences = sent_tokenize(text)
    tokenized = []

    for sentence in sentences:
        tokenized.extend(word_tokenize(sentence.lower()))

    return tokenized


def prepare_text(text):
    """Prepares a text by assigning features to a cleaned version.

    Args:
        text: A string to prepare.

    Returns:
        dictionary: Dictionary of strings to booleans indicating the
            existence of a certain feature.
    """

    tokenized = tokenize_full(text)
    return assign_features(clean_text(tokenized))


def clean_add(tweets, results, label):
    """Adds tweets to the given results list by features and classification.

    Args:
        tweets: List of Tweet objects.
        results: List to add into.
        label: Label to label these tweets as.

    Returns:
        list: List of tuples with the format (dictionary, category). The
            dictionary is a mapping from strings to booleans, indicating
            existence of a certain feature.
    """

    progress = ProgressBar()
    for tweet in progress(tweets):
        results.append((
            prepare_text(tweet.text),
            label
        ))


def classify_tweets():
    """Combines Scikit-Learn and NLTK with a SVM to classify tweets."""

    classifier = get_classifier()

    # TODO(Fix this to the whole database.)
    tweets = db.session.query(Tweet.text).limit(100).all()
    prepared_tweets = []

    widgets = [
        Percentage(),
        ' ', Bar(),
        ' ', ETA(),
    ]
    progress = ProgressBar(widgets=widgets)
    for tweet in progress(tweets):
        prepared_tweets.append(prepare_text(tweet.text))

    results = classifier.classify_many(prepared_tweets)
    probabilities = classifier.prob_classify_many(prepared_tweets)

    for i, v in enumerate(zip(results, probabilities)):
        print(str(i) + " : " + str(v))


def get_classifier():
    """Gets a classifier from the current data available.

    Returns:
        SKlearnClassifier: Trained classifier from given data.
    """

    classified = get_classify_set()

    shuffle(classified)
    test_size = int(len(classified) * .1)

    train_set = classified[test_size:]
    test_set = classified[:test_size]

    # TODO(Use a SVC instead of a LinearSVC for probabilities.)
    # TODO(Is there an advantage of LinearSVC?)
    classifier = SklearnClassifier(SVC(probability=True))
    classifier.train(train_set)

    # TODO(Make this into a neater lambda function.)
    test_features, test_label = [], []
    for item in test_set:
        test_features.append(item[0])
        test_label.append(item[1])

    classified_test = classifier.classify_many(test_features)
    print(classification_report(
        test_label, classified_test,
        labels=list(set(test_label)),
        target_names=CATEGORIES
    ))

    return classifier

if __name__ == "__main__":
    LOGGING.push("Starting to *classify* tweets.")
    classify_tweets()
    LOGGING.push("Finished *classifying* tweets.")
