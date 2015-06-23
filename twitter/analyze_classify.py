from colorama import Fore
from textblob.classifiers import NaiveBayesClassifier

from ..database import db_session

import models

CLASSIFICATIONS = ['sentiment', 'personal', 'convo', 'know']

# take all the classifications that have been classified and create the classifier
# and classify all of them by putting data into the _dist field

def classify(classification):
    # TODO: Fix this so it paginates through the results
    response_pos = db_session.query(models.Tweet).filter_by(**{classification + "_classify": "pos"}).all()
    response_neg = db_session.query(models.Tweet).filter_by(**{classification + "_classify": "neg"}).all()

    train_pos = [(response.text, "pos") for response in response_pos]
    train_neg = [(response.text, "neg") for response in response_neg]
    train = train_pos + train_neg

    cl = NaiveBayesClassifier(train)

    testing = db_session.query(models.Tweet).filter_by(**{classification + "_classify": None}).limit(100)
    # show accuracy of test set?
    # print("Getting accuracy of " + str(cl.accuracy(testing)))

    cl.show_informative_features(10)

    print("Printing the " + classification + " classifications...")

    for response in testing[100:200]:
        print(response.text)
        print(cl.classify(response.text) + " " + str(cl.prob_classify(response.text).prob("pos")))

if __name__ == "__main__":
    for classification in CLASSIFICATIONS:
        classify(classification)
