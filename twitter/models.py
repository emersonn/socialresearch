from twitter import db


class Trend(db.Model):
    __tablename__ = 'trend'

    id = db.Column(db.Integer, primary_key=True)

    stored = db.Column(db.DateTime)
    query = db.Column(db.String(400))
    name = db.Column(db.String(400))

    place = db.Column(db.String(400))

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

    tweet_id = db.Column(db.BigInteger, unique=True)

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

    @staticmethod
    def store_tweet(status):
        try:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]
        except TypeError:
            longitude = None
            latitude = None

        try:
            place = status.place.full_name
        except (TypeError, AttributeError):
            place = None

        store_tweet = Tweet(
            text=str(status.text.encode('unicode_escape')),

            tweet_id=status.id,
            user_id=int(status.user.id_str),
            screen_name=status.user.screen_name,

            number=int(status.id_str),
            created_at=status.created_at,

            favorite_count=status.favorite_count,
            retweet_count=status.retweet_count,

            longitude=longitude,
            latitude=latitude,
            place=place
        )

        db.session.add(store_tweet)
        db.session.commit()


class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100))


class Word(db.Model):
    __tablename__ = "word"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(1000))
    context = db.relationship('Tweet', secondary=tweet_word, backref="words")
