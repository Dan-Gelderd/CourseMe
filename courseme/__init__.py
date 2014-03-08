import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import basedir
import md5      #DJG - depricated, explore hashlib or passlib or some password storing package

app = Flask(__name__,
            static_folder="../static",
            static_url_path="/static")

app.config.from_object('config')

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
#lm.session_protection = "strong"   DJG - Need to consider this

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')

def hash_string(string):
    salted_hash = string + app.config['SECRET_KEY']
    return md5.new(salted_hash).hexdigest()

from courseme import views, models