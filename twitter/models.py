from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, BigInteger
from sqlalchemy.orm import relationship, backref

from ..database import Base

class Trend(Base):
    __tablename__ = 'trend'

    id = Column(Integer, primary_key = True)

    stored = Column(DateTime)
    query = Column(String(400))
    name = Column(String(400))

    place = Column(String(400))

class Tweet(Base):
    __tablename__ = 'tweet'

    id = Column(Integer, primary_key = True)

    text = Column(String(1000))
    user_id = Column(BigInteger)
    number = Column(BigInteger)
    created_at = Column(DateTime)

    favorite_count = Column(Integer)
    retweet_count = Column(Integer)

    longitude = Column(Float)
    latitude = Column(Float)

    trend_id = Column(Integer, ForeignKey('trend.id'))
    trend = relationship('Trend', backref = backref('tweet', order_by = id))

    place = Column(String(400))

    # is there a positive or negative sentiment in this tweet?
    sentiment_classify = Column(String(10))
    sentiment_dist = Column(Float)

    # does the user share any personal information in the tweet?
    personal_classify = Column(String(10))
    personal_dist = Column(Float)

    # is this person having a conversation with another person in this tweet
    # or directly talking about another person? using names, etc
    convo_classify = Column(String(10))
    convo_dist = Column(Float)

    # do you feel like you know this person through this tweet? can you tell what
    # type of person they are?
    know_classify = Column(String(10))
    know_dist = Column(Float)
