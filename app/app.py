#!flask/bin/python

import flask
from flask import g, url_for
from flask.ext.sqlalchemy import SQLAlchemy

import os
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.openid import OpenID
from config import basedir

import forms
import datamodel
import database
import datetime

app = flask.Flask(__name__,
            static_folder="../static",
            static_url_path="/static")

app.config.from_object('config')

db = SQLAlchemy(app)
import models
db.create_all()

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@lm.user_loader
def load_user(id):
    return models.User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/')
@app.route('/index')
#@login_required
def index():
    user = g.user
    posts = [
        { 
            'author': { 'nickname': 'John' }, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': { 'nickname': 'Susan' }, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]

    return flask.render_template('index.html',
        user = user,
        posts = posts)

@app.route('/module/<name>')
def module(name):
    
    module = datamodel.Module.find(name)
    user = datamodel.User.find("Student")
    try:
        usermodule = datamodel.UserModule.find(user, module)
    except KeyError:
        usermodule = datamodel.UserModule(user, module)

    authormodule = datamodel.UserModule.find(module.author, module)
    #tutormodule = datamodel.UserModule.find(module.author, module)    

    return flask.render_template('module.html',
                           module=module,
                           usermodule=usermodule,
                           authormodule=authormodule,
    )


@app.route('/star/<name>')
def starclick(name):
    
    module = datamodel.Module.find(name)
    user = datamodel.User.find("Student")
    try:
        usermodule = datamodel.UserModule.find(user, module)
    except KeyError:
        usermodule = datamodel.UserModule(user, module)

    usermodule.starred = not usermodule.starred
    usermodule.save()
    
    return usermodule.as_json()


@app.route('/vote/<name>')
def voteclick(name):
    
    module = datamodel.Module.find(name)
    user = datamodel.User.find("Student")
    try:
        usermodule = datamodel.UserModule.find(user, module)
    except KeyError:
        usermodule = datamodel.UserModule(user, module)
    
    newVote = int(flask.request.args.get("vote"))
    module.votes = module.votes - usermodule.vote + newVote       #DJG - Almost certainly a better way
    usermodule.vote = newVote
        
    usermodule.save()
    module.save
    
    return ""   #DJG - What is best return value when I don't care about the return result? Only thing I found that worked


@app.route('/objectives', methods = ['GET', 'POST'])
def objectives():
    objectives = models.Objective.query.all()
    form = forms.AddObjective()
    if form.validate_on_submit():
        objective = models.Objective(name=form.objective_name.data)
        db.session.add(objective)
        db.session.commit()
    return flask.render_template('objectives.html',
                                 form=form,
                                 objectives=objectives)


@app.route('/objectivedelete')
def objectivedelete():
    objective = models.Objective.query.filter_by(id = flask.request.args.get("objective_id")).first()
    db.session.delete(objective)
    db.commit
    objectives = models.Objective.query.all()
    return {"a": "A"}
   
   
@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return flask.redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        flask.session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])        
    return flask.render_template('login.html',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return flask.redirect(url_for('login'))
    user = models.User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
            nickname = models.User.make_unique_nickname(nickname)
        user = models.User(nickname = nickname, email = resp.email, role = models.ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in flask.session:
        remember_me = flask.session['remember_me']
        flask.session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return flask.redirect(flask.request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return flask.redirect(url_for('index'))


def run_devserver():
    app.run(debug=True)

if __name__ == "__main__":
    run_devserver()