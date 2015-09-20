from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import DateTime, ForeignKey, Float, BigInteger
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Trend(Base):
    __tablename__ = 'trend'

    id = Column(Integer, primary_key=True)

    stored = Column(DateTime)
    query = Column(String(400))
    name = Column(String(400))

    place = Column(String(400))

# TODO: Modify the association table's names
tag_table = Table(
    'tweet_tag',
    Base.metadata,
    Column('tweet_id', Integer, ForeignKey('tweet.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

word_table = Table(
    'word_table',
    Base.metadata,
    Column('word_id', Integer, ForeignKey('word.id')),
    Column('tweet_id', Integer, ForeignKey('tweet.id'))
)


class Tweet(Base):
    __tablename__ = 'tweet'

    id = Column(Integer, primary_key=True)

    text = Column(String(1000))
    user_id = Column(BigInteger)
    screen_name = Column(String(100))
    number = Column(BigInteger)
    created_at = Column(DateTime)

    favorite_count = Column(Integer)
    retweet_count = Column(Integer)

    longitude = Column(Float)
    latitude = Column(Float)

    trend_id = Column(Integer, ForeignKey('trend.id'))
    trend = relationship('Trend', backref=backref('tweet', order_by=id))

    place = Column(String(400))

    # Literally sentiment of the tweet
    sentiment_classify = Column(String(10))
    sentiment_dist = Column(Float)

    # Does the person share any personal information about themselves?
    personal_classify = Column(String(10))
    personal_dist = Column(Float)

    # Is there a reasonable conversation going on in this tweet?
    convo_classify = Column(String(10))
    convo_dist = Column(Float)

    # Do you feel like you get to know this person through this tweet?
    know_classify = Column(String(10))
    know_dist = Column(Float)

    analyzed_date = Column(DateTime)

    tags = relationship('Tag', secondary=tag_table, backref="tweets")


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    tag = Column(String(100))


class Word(Base):
    __tablename__ = "word"

    id = Column(Integer, primary_key=True)
    word = Column(String(1000))
    context = relationship('Tweet', secondary=word_table, backref="words")
