from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from courseme import app, db, lm, oid
import forms
from models import User, ROLE_USER, ROLE_ADMIN, Objective
from datetime import datetime
import datamodel

#admin
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/')
@app.route('/index')
@login_required
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
    return render_template('index.html',
        title = 'Home',
        user = user,
        posts = posts)

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



#objectives
@app.route('/objectives', methods = ['GET', 'POST'])
def objectives():
    form = forms.AddObjective()
    if form.validate_on_submit():
        objective = Objective(name=form.objective_name.data)
        db.session.add(objective)
        db.session.commit()
    objectives = Objective.query.all()
    return render_template('objectives.html',
                                 form=form,
                                 objectives=objectives)


@app.route('/objectivedelete')
def objectivedelete():
    objective = Objective.query.filter_by(id = request.args.get("objective_id")).first()
    #import pdb; pdb.set_trace() # <-- DJG - this is temporary!
    db.session.delete(objective)
    db.session.commit()
    objectives = Objective.query.all()
    return {"a": "A"}


#modules
@app.route('/module/<name>')
def module(name):
    
    module = datamodel.Module.find(name)
    user = datamodel.User.find("Student")
    try:
        usermodule = datamodel.UserModule.find(user, module)
    except KeyError:
        usermodule = datamodel.UserModule(user, module)

    authormodule = datamodel.UserModule.find(module.author, module)

    return render_template('module.html',
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
