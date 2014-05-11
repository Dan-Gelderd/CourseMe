from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, PasswordField, BooleanField, HiddenField, FileField, SelectMultipleField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo

class SignupForm(Form):
    email = TextField('Email address', validators=[
                Required('Please provide a valid email address'),
                Email(message=(u'That\'s not a valid email address'))])
    password = PasswordField('Pick a secure password', validators=[
                Required('Please enter a password'),
                Length(min=6, message=(u'Password must be at least 6 characters'))])
    confirm_password = PasswordField('Confirm password', validators=[
                EqualTo('password', message='Password confirmation did not match')])
    username = TextField('Name', validators=[Required()])
    agree = BooleanField('By signing up your agree to follow our <a href="#">Terms and Conditions</a>',
                validators=[Required(u'You must agree the Terms of Service')])    
    remember_me = BooleanField('remember_me', default = False)

class LoginForm(Form):
    email = TextField('Email address', validators=[
                Required('Please enter the email address you used to sign up'),
                Email(message=(u'That\'s not a valid email address'))])
    password = PasswordField('Enter password', validators=[
                Required('Please enter your password'),
                Length(min=6, message=(u'Password must be at least 6 characters'))])
    remember_me = BooleanField('remember_me', default = False)

class EditObjective(Form):
    edit_objective_id = HiddenField()
    edit_objective_name = TextField('Objective', validators = [
                Regexp(r'\w'),                  #DJG - need to exclude commas in current implementation of ajax calls but this isn't working
                Required('Enter a description of the objective'),
                Length(min=4, message=(u'Description must be at least 4 characters'))])
    new_prerequisite = TextField('Prerequisites', validators=[])
                #Regexp(r'\w', message=(u'Can only use spaces, numbers and letters in the description'))])

class EditModule(Form):
    name = TextField('Module name', validators=[Required('Please enter a name for your module')])
    brief_description = TextAreaField('Brief description')
    notes = TextAreaField('Notes')
    material = FileField('Material', validators=[Required()])

class EditCourse(Form):
    name = TextField('Course name', validators=[Required('Please enter a name for your course')])
    brief_description = TextAreaField('Brief description', validators=[Required('Please enter a brief description of your course')])
    notes = TextAreaField('Notes')
    