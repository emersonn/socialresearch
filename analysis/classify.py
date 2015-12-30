from sys import exit

from prettylog import PrettyLog

from twitter import db

from twitter.models import Tweet

# TODO(Abstract this out into a settings file.)
CLASSIFICATIONS = ['sentiment', 'personal', 'convo', 'know']

CLASSIFICATION_CATEGORIES = {
    'sentiment': ['pos', 'neg', 'no']
}

CLASSIFICATION_SUFFIX = "_classify"

LOGGING = PrettyLog()


def classify(classification):
    model_attr = classification + CLASSIFICATION_SUFFIX

    choices = ""
    for i, choice in enumerate(CLASSIFICATION_CATEGORIES[classification]):
        choices += ", " if i > 0 else ""
        choices += str(i + 1) + " = " + choice

    # TODO(Add pagination for infinite classification until exit.)
    response = (
        db.session.query(Tweet)
        .filter_by(**{model_attr: None})
        .limit(100)
    )

    for row in response:
        LOGGING.push(
            "*" + str(row.tweet_id) + "*: " +
            LOGGING.clean(row.text.decode('unicode-escape'))
        )

        LOGGING.push(
            "Currently classifying the @" + classification + "@."
        )

        user = raw_input(
            "Classification? (" + choices
            + ") (exit to exit) "
        )

        if user == "exit":
            exit()

        user = int(user) - 1

        if user not in range(
            len(CLASSIFICATION_CATEGORIES[classification])
        ):
            print("Was not any of the choices, going to the next tweet.")
            continue

        user = CLASSIFICATION_CATEGORIES[classification][user]
        setattr(row, model_attr, user)

        db.session.add(row)
        db.session.commit()

        LOGGING.push("Classified as *" + user + "*.")

if __name__ == "__main__":
    classification = raw_input(
        "What type are we classifying? (" + ", ".join(CLASSIFICATIONS) + ") "
    )

    classify(classification)
