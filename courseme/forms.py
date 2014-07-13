from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, PasswordField, BooleanField, HiddenField, FileField, SelectMultipleField, RadioField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, url
from wtforms.fields.html5 import URLField
from wtforms.fields import FieldList

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
    dynamic_list_select = SelectMultipleField('Prerequisites', choices=[])
    authors = FieldList(TextField('Name'))      #DJG - Try this as way of geting proper ordered list back from form

class EditModule(Form):
    edit_module_id = HiddenField()                  #DJG - don't know if I need this
    name = TextField('Module name', validators=[Required('Please enter a name for your module')])
    description = TextAreaField('Brief description')
    notes = TextAreaField('Notes')
    material_type = RadioField('Material Type',
                                 choices=[('Lecture', 'Lecture'), ('Exercise', 'Exercise'), ('Course', 'Course (select individual modules to include later)')],
                                 default='Lecture',
                                 validators = [Required('Please specify what type of material you are creating')])
    material_source = RadioField('Material Source',
                                 choices=[('upload', 'Upload video'), ('youtube', 'youtube link')],
                                 default='upload')     #validators = [Required('Please specify how you are providing the material')])
    material_upload = FileField('Select File')         #DJG - would be nice to have these be required when they apply     #validators=[Required('Please upload your material')])
    material_youtube = URLField('Enter URL')                            #validators=[url, Required('Please provide a link to your material')])
    subtitles = BooleanField('Subtitles', default = False)
    easy_language = BooleanField('Simple Language', default = False)
    extension = BooleanField('Extension Material', default = False)
    for_teachers = BooleanField('For Teachers', default = False)
