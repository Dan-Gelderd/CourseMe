from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from courseme import app, db, lm, hash_string
import forms
from models import User, ROLE_USER, ROLE_ADMIN, Objective
from datetime import datetime
import json
import datamodel
#import pdb; pdb.set_trace()

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
#@login_required
def index():
    title = "CourseMe"
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
        title = title,
        user = user,
        posts = posts)


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    title = 'CourseMe - Sign up'
    form = forms.SignupForm()
    if form.validate_on_submit():
        email_exist = User.query.filter_by(email=form.email.data).count()
        if email_exist:
            form.email.errors.append('This email address has already been registered')
            return render_template('signup.html', form = form, title = title)
        else:
            user = User(email=form.email.data,
                        password=hash_string(form.password.data),
                        username=form.username.data,
                        time_registered=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        role = ROLE_USER)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember = form.remember_me.data)
            flash("Successfully signed up.")
            return redirect(request.args.get("next") or url_for("index"))
    return render_template('signup.html', form=form, title=title)


@app.route("/login", methods=["GET", "POST"])
def login():
    title = 'CourseMe - Login'
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is None:
            form.email.errors.append('Email not registered')
            return render_template('login.html', form = form, title=title)
        if user.password != hash_string(form.password.data):
            form.password.errors.append('Incorrect password')
            return render_template('login.html', form = form, title=title)
        login_user(user, remember = form.remember_me.data)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("index"))
    return render_template('login.html', form=form, title=title)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#objectives
@app.route('/objectives', methods = ['GET', 'POST'])
def objectives():
    title = "CourseMe - Objectives"
    form = forms.AddObjective()
    if form.validate_on_submit():
        newObjectiveName = form.objective_name.data
        objective = Objective(name=newObjectiveName)
        db.session.add(objective)
        db.session.commit()
    objectives = Objective.query.all()
    return render_template('objectives.html',
                           title=title,
                           form=form,
                           objectives=objectives)


@app.route('/objectivedelete')
def objectivedelete():
    objective = Objective.query.filter_by(id = request.args.get("objective_id")).first()
    db.session.delete(objective)
    db.session.commit()
    return ""

@app.route('/objectiveedit')
def objectiveedit():
    objective = Objective.query.filter_by(id = request.args.get("objective_id")).first()
    return json.dumps(objective.as_dict(), sort_keys=True, separators=(',',':'))


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
