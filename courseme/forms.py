from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, HiddenField, FileField, SelectMultipleField
from wtforms.validators import Required, Length, Email, Regexp

class SignupForm(Form):
    email = TextField('Email address', validators=[
                Required('Please provide a valid email address'),
                Email(message=(u'That\'s not a valid email address'))])
    password = PasswordField('Pick a secure password', validators=[
                Required('Please enter a password'),
                Length(min=6, message=(u'Password must be at least 6 characters'))])
    username = TextField('Choose your username', validators=[Required()])
    agree = BooleanField('By signing up your agree to follow our <a href="#">Terms of Services</a>',
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

class AddUpdateObjective(Form):
    edit_objective_id = HiddenField()
    edit_objective_name = TextField('Objective', validators = [
                Regexp(r'\w'),                  #DJG - need to exclude commas in current implementation of ajax calls but this isn't working
                Required('Enter a description of the objective'),
                Length(min=4, message=(u'Description must be at least 4 characters'))])
    new_prerequisite = TextField('Prerequisites', validators=[])
                #Regexp(r'\w', message=(u'Can only use spaces, numbers and letters in the description'))])


class CreateModule(Form):
    name = TextField('Module name', validators=[Required()])
    objectives = SelectMultipleField('Objectives')
    material = FileField('Material')
    tags = TextField('Tags', validators=[
            Length(min=2, message=(u'The tag at least having 2 characters length'))
            ])