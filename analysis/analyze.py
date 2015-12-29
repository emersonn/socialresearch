"""
Analysis Script
Emerson Matson

Analyzes the Tweets in the database by a number of features for data
representation.
"""

from prettylog import PrettyLog

LOGGING = PrettyLog()


def classify_tweets():
    """Combines Scikit-Learn and NLTK with a SVM to classify tweets."""

    pass

if __name__ == "__main__":
    LOGGING.push("Starting to *classify* tweets.")
    classify_tweets()
    LOGGING.push("Finished *classifying* tweets.")
