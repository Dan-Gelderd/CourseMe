from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.uploads import UploadSet, configure_uploads, patch_request_class
from flask_mail import Mail
from flask_restless import APIManager
from flask_util_js import FlaskUtilJs       #DJG - for stuff like url_for in javascript
from flask.ext.moment import Moment
from flask.ext.bootstrap import Bootstrap
from config import config


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'auth.login'
lm.session_protection = "strong"   #DJG - Need to consider this
api_manager = APIManager()
fujs = FlaskUtilJs()
lectures = UploadSet('lectures', extensions=('mp4'))

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    lm.init_app(app)
    api_manager.init_app(app, flask_sqlalchemy_db=db)
    fujs.init_app(app)
    configure_uploads(app, (lectures))
    patch_request_class(app, 8 * 1024 * 1024)        # 16 megabytes

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from institutions import institutions as institutions_blueprint
    app.register_blueprint(institutions_blueprint, url_prefix='/institutions')

    return app