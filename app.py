import datetime
import random

from flask import Flask, jsonify, send_file
from sqlalchemy import func

from twitter.config import PRESET_TAGS
from twitter.models import Tweet, Word, Tag
from database import db_session

app = Flask(__name__)
app.config.from_object('app_settings')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    return send_file('static/index.html')


@app.route('/api/stats/')
def stats():
    tweet_count = db_session.query(func.count(Tweet.id)).scalar()
    tweet_sample = random.sample(xrange(0, tweet_count), 1000)
    random_tweets = db_session.query(Tweet).filter(Tweet.id.in_(tweet_sample))

    # TODO: Abstract these calculations, make it more efficient
    tweet_text = [len(tweet.text) for tweet in random_tweets]
    tweet_text_average = round(
        reduce(lambda x, y: x + y, tweet_text) / float(len(tweet_text)), 2
    )

    tweet_retweet = [tweet.retweet_count for tweet in random_tweets]
    tweet_retweet_average = round(
        reduce(lambda x, y: x + y, tweet_retweet) / float(len(tweet_retweet)),
        5
    )

    return jsonify(
        {
            'tweet_count': tweet_count,
            'user_count': tweet_retweet_average,
            'tweet_average': tweet_text_average
        }
    )


@app.route('/api/words/')
def words():
    # TODO: Cache, preprocess, index, prune?
    #       Improve the efficiency of this calculation
    words = (
        db_session.query(Word)
        .join(Word.context)
        .group_by(Word.id)
        .having(func.length(Word.word) > 5)
        .order_by(func.count(Tweet.id).desc())
        .limit(20).all()
    )

    word_stats = {'words': [word.word for word in words], 'data': []}

    for word in words:
        word_stats['data'].append(len(word.context))

    current_time = datetime.datetime.utcnow()
    date_stats = {'labels': [], 'data': []}
    date_sentiment = {'labels': [], 'data': []}

    # TODO: Very inefficient way to go about it
    for days in range(0, 31):
        days_ago = current_time - datetime.timedelta(days=days)

        # extend to an existing?
        if days_ago.date() != datetime.datetime.today().date():
            date_format = days_ago.strftime("%A (%D)")
        else:
            date_format = days_ago.strftime("Today (%D)")
        date_stats['labels'].append(date_format)
        date_sentiment['labels'].append(date_format)

        tweets = (
            db_session.query(Tweet)
            .filter(func.DATE(Tweet.created_at) == days_ago.date())
            .all()
        )
        date_stats['data'].append(len(tweets))

        sentiment = 0.0
        for tweet in tweets:
            if tweet.sentiment_dist is not None:
                sentiment += tweet.sentiment_dist
        try:
            date_sentiment['data'].append(sentiment/len(tweets))
        except ZeroDivisionError:
            date_sentiment['data'].append(0)
        # strftime ("%A (%D)")

    query = (
        db_session.query(Word)
        .filter(Word.word.contains("#"))
        .join(Word.context)
        .group_by(Word.id)
        .order_by(func.count(Tweet.id).desc())
        .limit(20)
        .all()
    )

    hashtag_sentiment = {'labels': [], 'data': []}
    hashtag_distribution = {'labels': [], 'data': []}

    # TODO: Abstract this out
    for hashtag in query:
        hashtag_sentiment['labels'].append(hashtag.word[:10])
        hashtag_distribution['labels'].append(hashtag.word[:10])

        tweets = hashtag.context
        sentiment = 0.0
        favorites = 0.0

        for tweet in tweets:
            if tweet.sentiment_dist is not None:
                sentiment += tweet.sentiment_dist
                favorites += tweet.favorite_count
        try:
            hashtag_sentiment['data'].append(sentiment/len(tweets))
            hashtag_distribution['data'].append(favorites/len(tweets))
        except ZeroDivisionError:
            hashtag_sentiment['data'].append(0)
            hashtag_distribution['data'].append(0)

    return jsonify(
        {
            'word_stats': word_stats,
            'date_stats': date_stats,
            'date_sentiment': date_sentiment,
            'hashtag_sentiment': hashtag_sentiment,
            'hashtag_distribution': hashtag_distribution
        }
    )


@app.route('/api/religion/')
def religion():
    pie_chart = {'labels': [], 'data': []}
    for tag in PRESET_TAGS.keys():
        pie_chart['labels'].append(tag)
        pie_chart['data'].append(
            len(db_session.query(Tag).having(Tag.tag == tag).one().tweets)
        )

    return jsonify({'pie_chart': pie_chart})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
