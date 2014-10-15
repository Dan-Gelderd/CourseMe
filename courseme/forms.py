from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, TextAreaField, PasswordField, BooleanField, HiddenField, FileField, SelectMultipleField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, url
from wtforms.fields.html5 import URLField
from wtforms.fields import FieldList
from models import Module, Objective

class SignupForm(Form):
    email = TextField('Email address', validators=[
                DataRequired('Please provide a valid email address'),
                Email(message=(u'That\'s not a valid email address'))])
    password = PasswordField('Pick a secure password', validators=[
                DataRequired('Please enter a password'),
                Length(min=6, message=(u'Password must be at least 6 characters'))])
    confirm_password = PasswordField('Confirm password', validators=[
                EqualTo('password', message='Password confirmation did not match')])
    username = TextField('Name', validators=[DataRequired()])
    agree = BooleanField('By signing up your agree to follow our <a href="#">Terms and Conditions</a>',
                validators=[DataRequired(u'You must agree the Terms of Service')])    
    remember_me = BooleanField('remember_me', default = False)
    recaptcha = RecaptchaField()

class LoginForm(Form):
    email = TextField('Email address', validators=[
                DataRequired('Please enter the email address you used to sign up'),
                Email(message=(u'That\'s not a valid email address'))])
    password = PasswordField('Enter password', validators=[
                DataRequired('Please enter your password'),
                Length(min=6, message=(u'Password must be at least 6 characters'))])
    remember_me = BooleanField('remember_me', default = False)

class EditObjective(Form):
    edit_objective_id = HiddenField()
    edit_objective_name = TextField('Objective', validators = [
                DataRequired('Enter a description of the objective'),
                Length(min=4, message=(u'Description must be at least 4 characters'))])
    edit_objective_subject = SelectField('Subject', choices=[('Mathematics','Mathematics'),('Biology','Biology')])
    edit_objective_prerequisites = SelectMultipleField('Prerequisites', choices=[])
    #authors = FieldList(TextField('Name'))      #DJG - Try this as way of geting proper ordered list back from form

class EditModule(Form):
    edit_module_id = HiddenField()                  #DJG - don't know if I need this
    name = TextField('Module name', validators=[DataRequired('Please enter a name for your module')])
    description = TextAreaField('Brief description')
    notes = TextAreaField('Notes')
    module_objectives = SelectMultipleField('Objectives', choices=[])
    material_type = RadioField('Material Type',
                                 choices=[('Lecture', 'Lecture'), ('Exercise', 'Exercise'), ('Course', 'Course (select individual modules to include later)')],
                                 default='Lecture',
                                 validators = [DataRequired('Please specify what type of material you are creating')])
    material_source = RadioField('Material Source',
                                 choices=[('upload', 'Upload video'), ('youtube', 'youtube link')],
                                 default='upload')     #validators = [DataRequired('Please specify how you are providing the material')])
    material_upload = FileField('Select File')         #DJG - would be nice to have these be DataRequired when they apply     #validators=[DataRequired('Please upload your material')])
    material_youtube = URLField('Enter URL')                            #validators=[url, DataRequired('Please provide a link to your material')])
    subtitles = BooleanField('Subtitles', default = False)
    easy_language = BooleanField('Simple Language', default = False)
    extension = BooleanField('Extension Material', default = False)
    for_teachers = BooleanField('Ideas for Teachers', default = False)

class EditQuestion(Form):
    edit_question_id = HiddenField()
    question = TextAreaField('Question')
    answer = TextAreaField('Answer')
    #objective = SelectField('Objectives', choices=Objective.Choices())
    extension = BooleanField('Extension Material', default = False)
    question_objectives = SelectMultipleField('Objectives', choices=[])

class EditGroup(Form):
    edit_group_id = HiddenField()
    edit_group_name = TextField('Group Name', validators = [DataRequired('Enter a group name')])
    edit_group_members = SelectMultipleField('Members', choices=[])

class EditScheme(Form):
    edit_scheme_id = HiddenField()
    edit_scheme_name = TextField('Scheme Name', validators = [DataRequired('Enter a name for this scheme of work')])
    edit_scheme_objectives = SelectMultipleField('Objectives', choices=[])
    
class SendMessage(Form):
    message_type = RadioField('Group or Individual Message',
                                 choices=[('Individual', 'Individual'), ('Group', 'Group')],
                                 default='Individual',
                                 validators = [DataRequired('Please specify whether you are sending an individual or a group message')])
    message_to = TextField('To', validators = [DataRequired('Enter a recipient or group of recipients for your message')])
    message_subject = TextField('Message Subject')
    message_body = TextAreaField('Message Content')
    request_access = BooleanField("Request to view students' progress", default = False)
    recommended_material = SelectField('Recommend Material', choices=Module.RecommendChoices())