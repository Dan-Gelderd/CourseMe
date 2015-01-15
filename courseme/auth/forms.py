from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextAreaField, PasswordField, BooleanField, HiddenField, FileField, SelectMultipleField, \
    SelectField, RadioField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, url, Optional
from wtforms.fields.html5 import URLField
from wtforms.fields import FieldList
from wtforms import ValidationError
from .. models import Module, Objective, User


class SignupForm(Form):
    email = StringField('Email address', validators=[
        DataRequired('Please provide a valid email address'),
        Email(message=(u'That\'s not a valid email address'))])
    password = PasswordField('Pick a secure password', validators=[
        DataRequired('Please enter a password'),
        Length(min=6, message=(u'Password must be at least 6 characters'))])
    confirm_password = PasswordField('Confirm password', validators=[
        EqualTo('password', message='Password confirmation did not match')])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=1, message='Username is too short'),
        Regexp('^[A-Za-z][A-Za-z0-9_.\- ]*$', 0, 'Usernames must have only letters, numbers, dots, dashes, underscores, or spaces')])
    forename = StringField('Forename', validators=[
        Optional(),
        Length(min=1, message='Forename is too short'),
        Regexp('^[A-Za-z][A-Za-z0-9_.\- ]*$', 0, 'Forenames must have only letters, numbers, dots, dashes, underscores, or spaces')])
    surname = StringField('Surname', validators=[
        Optional(),
        Length(min=1, message='Forename is too short'),
        Regexp('^[A-Za-z][A-Za-z0-9_.\- ]*$', 0, 'Surnames must have only letters, numbers, dots, dashes, underscores, or spaces')])
    agree = BooleanField('By signing up your agree to follow our <a href="#">Terms and Conditions</a>',
                         validators=[DataRequired(u'You must agree the Terms of Service')])
    remember_me = BooleanField('remember_me', default=False)
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign-up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This email address has already been registered')


class LoginForm(Form):
    email = StringField('Email address', validators=[
        DataRequired('Please enter the email address you used to sign up'),
        Email(message=(u'That\'s not a valid email address'))])
    password = PasswordField('Enter password', validators=[
        DataRequired('Please enter your password'),
        Length(min=6, message=(u'Password must be at least 6 characters'))])
    remember_me = BooleanField('remember_me', default=False)