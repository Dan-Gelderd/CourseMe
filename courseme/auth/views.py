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
        user = User(email=form.email.data,
                    password=form.password.data,
                    name=form.username.data,
                    forename=form.forename.data,
                    surname=form.surname.data,
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
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash("Logged in successfully.")
            return redirect(request.args.get('next') or url_for('main.index'))
            # DJG - next redirect doesn't seem to work eg. createmodule page
        else:
            form.password.errors.append('Incorrect password')
    return render_template('auth/login.html', form=form, title=title)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = forms.PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.user_by_email(form.email.data)
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = forms.PasswordResetForm()
    if form.validate_on_submit():
        user = User.user_by_email(form.email.data)
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
