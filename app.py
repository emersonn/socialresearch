import datetime, random

from flask import Flask, jsonify, send_file
from sqlalchemy import func
# from sqlalchemy.sql.expression import func

from twitter.models import Tweet, Word, Tag
from database import db_session

app = Flask(__name__)
# app.config.from_object('app_settings')

# DEBUG IS ON
app.debug = True

# TODO: Fix this by abstracting it out of analyze and app
PRESET_TAGS = {
    'Christian': ['God', 'Bible', 'Jesus', 'Jesus Christ', 'Church', 'Amen', 'Baptism', 'Christ', 'Holy Easter', 'Easter Sunday', 'Holy Spirit'],
    'Muslim': ['Koran', "Quran", "Q'uran", "Allah", "Mosque", 'Allahu Akbar', 'Ramadan', "Jumu'ah"],
    'Buddhist': ['Arahat', 'asura', 'Buddha', 'dharma', 'four noble truths', 'mantra', 'nirvana', 'Tao'],
    'Hindu': ['Brahman', 'Ishvara', 'Atman', 'Maya', 'Samsara', 'Niti shastra', 'Asteya', 'Astika', 'Vishnu', 'Shiva', 'Vedas']
}

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/api/stats/')
def stats():
    random_tweets = [len(tweet.text) for tweet in db_session.query(Tweet).order_by(func.rand()).limit(1000)]
    tweet_average = round(reduce(lambda x, y: x + y, random_tweets) / float(len(random_tweets)), 2)

    return jsonify({'tweet_count': db_session.query(Tweet).count() + random.randint(1, 10),
        'user_count': db_session.query(Tweet).group_by(Tweet.user_id).count() + random.randint(1, 10),
        'tweet_average': tweet_average})

@app.route('/api/words/')
def words():
    words = (db_session.query(Word)
                .join(Word.context)
                .group_by(Word.id)
                .having(func.length(Word.word) > 4)
                .order_by(func.count(Tweet.id).desc())
                .limit(20).all())

    word_stats = {'words': [word.word for word in words], 'data': []}

    for word in words:
        word_stats['data'].append(len(word.context))

    current_time = datetime.datetime.utcnow()
    date_stats = {'labels': [], 'data': []}
    date_sentiment = {'labels': [], 'data': []}

    for days in range(0, 31):
        days_ago = current_time - datetime.timedelta(days = days)

        # extend to an existing?
        if days_ago.date() != datetime.datetime.today().date():
            date_format = days_ago.strftime("%A (%D)")
        else:
            date_format = days_ago.strftime("Today (%D)")
        date_stats['labels'].append(date_format)
        date_sentiment['labels'].append(date_format)

        tweets = db_session.query(Tweet).filter(func.DATE(Tweet.created_at) == days_ago.date()).all()
        date_stats['data'].append(len(tweets))

        sentiment = 0.0
        for tweet in tweets:
            if tweet.sentiment_dist != None:
                sentiment += tweet.sentiment_dist
        try:
            date_sentiment['data'].append(sentiment/len(tweets))
        except ZeroDivisionError:
            date_sentiment['data'].append(0)
        # strftime ("%A (%D)")

    query = db_session.query(Word).filter(Word.word.contains("#")).join(Word.context).group_by(Word.id).order_by(func.count(Tweet.id).desc()).limit(20).all()
    hashtag_sentiment = {'labels': [], 'data': []}

    # TODO: Abstract this out
    for hashtag in query:
        hashtag_sentiment['labels'].append(hashtag.word[:10])

        tweets = hashtag.context
        sentiment = 0.0

        for tweet in tweets:
            if tweet.sentiment_dist != None:
                sentiment += tweet.sentiment_dist
        try:
            hashtag_sentiment['data'].append(sentiment/len(tweets))
        except ZeroDivisionError:
            hashtag_sentiment['data'].append(0)

    return jsonify({'word_stats': word_stats, 'date_stats': date_stats, 'date_sentiment': date_sentiment, 'hashtag_sentiment': hashtag_sentiment})

@app.route('/api/religion/')
def religion():
    pie_chart = {'labels': [], 'data': []}
    for tag in PRESET_TAGS.keys():
        pie_chart['labels'].append(tag)
        pie_chart['data'].append(len(db_session.query(Tag).having(Tag.tag == tag).one().tweets))

    return jsonify({'pie_chart': pie_chart})

if __name__ == '__main__':
    app.run()
