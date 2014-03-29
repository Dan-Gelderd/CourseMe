import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.uploads import UploadSet, configure_uploads, patch_request_class
from config import basedir
import md5      #DJG - depricated, explore hashlib or passlib or some password storing package
from flask_util_js import FlaskUtilJs       #DJG - for stuff like url_for in javascript

app = Flask(__name__)

app.config.from_object('config')

fujs = FlaskUtilJs(app)

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
#lm.session_protection = "strong"   DJG - Need to consider this

lectures = UploadSet('lectures', extensions=('mp4'))
configure_uploads(app, (lectures))
patch_request_class(app, 8 * 1024 * 1024)        # 16 megabytes

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