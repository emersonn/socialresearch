from flask import Flask

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('twitter.app_settings')

db = SQLAlchemy(app)

from twitter import models  # NOQA
from twitter import views  # NOQA
