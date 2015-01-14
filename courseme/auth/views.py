from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from courseme import db, lm
from . import auth
import forms
from .. models import User, ROLE_USER, ROLE_ADMIN, Subject
from datetime import datetime
import json, operator
from .. email import send_email
# import pdb; pdb.set_trace()        #DJG - remove

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = obj.isoformat()
        else:
            encoded_object = json.JSONEncoder.default(self, obj)
        return encoded_object


@auth.before_app_request
def before_request():
    g.user = current_user  # DJG - Could scrap this and just use current_user directly?
    g.subjects = Subject.query.all()        #DJG - Needed to populate the subject dropdown at the top of each page - look for alternatives
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    title = 'CourseMe - Sign up'
    form = forms.SignupForm()
    if form.validate_on_submit():
        email_exist = User.query.filter_by(email=form.email.data).count()
        if email_exist:
            form.email.errors.append('This email address has already been registered')
            redirect(url_for('.login'))
        else:
            user = User(email=form.email.data,
                        password=form.password.data,
                        name=form.username.data,
                        time_registered=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        role=ROLE_USER)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            flash("Successfully signed up.")
            return redirect(request.args.get("next") or url_for("main.index"))
    return render_template('auth/signup.html', form=form, title=title)


@auth.route("/login", methods=["GET", "POST"])
def login():
    title = 'CourseMe - Login'
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.user_by_email(form.email.data)
        if user is None:
            form.email.errors.append('Email not registered')
            return render_template('auth/login.html', form=form, title=title)
        if not user.verify_password(form.password.data):
            form.password.errors.append('Incorrect password')
            return render_template('auth/login.html', form=form, title=title)
        login_user(user, remember=form.remember_me.data)
        flash("Logged in successfully.")
        return redirect(request.args.get('next') or url_for('main.index'))
         # DJG - next redirect doesn't seem to work eg. createmodule page
    return render_template('auth/login.html', form=form, title=title)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
