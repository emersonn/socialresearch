from twitter import db


class Trend(db.Model):
    __tablename__ = 'trend'

    id = db.Column(db.Integer, primary_key=True)

    stored = db.Column(db.DateTime)
    query = db.Column(db.String(400))
    name = db.Column(db.String(400))

    place = db.Column(db.String(400))

# TODO(Modify the association db.Table's names)
tweet_tag = db.Table(
    'tweet_tag',
    db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

tweet_word = db.Table(
    'word_db.Table',
    db.Column('word_id', db.Integer, db.ForeignKey('word.id')),
    db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id'))
)


class Tweet(db.Model):
    __tablename__ = 'tweet'

    id = db.Column(db.Integer, primary_key=True)

    text = db.Column(db.String(1000))

    # TODO(Need to store tweet id to make it unique.)
    # tweet_id = db.Column(db.BigInteger, unique=True)

    user_id = db.Column(db.BigInteger)
    screen_name = db.Column(db.String(100))
    number = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime)

    favorite_count = db.Column(db.Integer)
    retweet_count = db.Column(db.Integer)

    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)

    trend_id = db.Column(db.Integer, db.ForeignKey('trend.id'))
    trend = db.relationship('Trend', backref=db.backref('tweet', order_by=id))

    place = db.Column(db.String(400))

    # Literally sentiment of the tweet
    sentiment_classify = db.Column(db.String(10))
    sentiment_dist = db.Column(db.Float)

    # Does the person share any personal information about themselves?
    personal_classify = db.Column(db.String(10))
    personal_dist = db.Column(db.Float)

    # Is there a reasonable conversation going on in this tweet?
    convo_classify = db.Column(db.String(10))
    convo_dist = db.Column(db.Float)

    # Do you feel like you get to know this person through this tweet?
    know_classify = db.Column(db.String(10))
    know_dist = db.Column(db.Float)

    analyzed_date = db.Column(db.DateTime)

    tags = db.relationship('Tag', secondary=tweet_tag, backref="tweets")


class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100))


class Word(db.Model):
    __tablename__ = "word"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(1000))
    context = db.relationship('Tweet', secondary=tweet_word, backref="words")
