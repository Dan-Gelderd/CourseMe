from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, TextAreaField, PasswordField, BooleanField, HiddenField, FileField, SelectMultipleField, \
    SelectField, RadioField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, url, optional
from wtforms.fields.html5 import URLField
from wtforms.fields import FieldList
from .. models import Module, Objective, User

from courseme.util.wtform_utils import blank_to_none


class EditObjective(Form):
    id = HiddenField(filters=[blank_to_none])
    name = TextField('Objective', validators=[
        DataRequired('Enter a description of the objective'),
        Length(min=4, message=(u'Description must be at least 4 characters'))])
    topic_id = SelectField('Topic')
    prerequisites = SelectMultipleField('Prerequisites', choices=[])
    # authors = FieldList(TextField('Name'))      #DJG - Try this as way of geting proper ordered list back from form

    def __init__(self, topic_choices, **kwargs):
        """Construct a new EditObjective form.

        :param topic_choices: a list of 2-tuples representing the IDs and
                              labels of available Topics.
        """
        super(EditObjective, self).__init__(**kwargs)
        self.topic_id.choices = topic_choices


class EditModule(Form):
    edit_module_id = HiddenField()  # DJG - don't know if I need this
    name = TextField('Module name', validators=[DataRequired('Please enter a name for your module')])
    description = TextAreaField('Brief description')
    notes = TextAreaField('Notes')
    module_objectives = SelectMultipleField('Objectives', choices=[])
    material_type = RadioField('Material Type',
                               choices=[('Lecture', 'Lecture'), ('Exercise', 'Exercise'),
                                        ('Course', 'Course (select individual modules to include later)')],
                               default='Lecture',
                               validators=[DataRequired('Please specify what type of material you are creating')])
    material_source = RadioField('Material Source',
                                 choices=[('upload', 'Upload video'), ('youtube', 'youtube link')],
                                 default='upload')  # validators = [DataRequired('Please specify how you are providing the material')])
    material_upload = FileField(
        'Select File')  # DJG - would be nice to have these be DataRequired when they apply     #validators=[DataRequired('Please upload your material')])
    material_youtube = URLField(
        'Enter URL')  # validators=[url, DataRequired('Please provide a link to your material')])
    subtitles = BooleanField('Subtitles', default=False)
    easy_language = BooleanField('Simple Language', default=False)
    extension = BooleanField('Extension Material', default=False)
    for_teachers = BooleanField('Ideas for Teachers', default=False)


class EditQuestion(Form):
    edit_question_id = HiddenField()
    question = TextAreaField('Question')
    answer = TextAreaField('Answer')
    # objective = SelectField('Objectives', choices=Objective.Choices())
    extension = BooleanField('Extension Material', default=False)
    visually_impaired = BooleanField('Audio Assistance', default=False)
    question_objectives = SelectMultipleField('Objectives', choices=[])


class EditGroup(Form):
    edit_group_id = HiddenField()
    edit_group_name = TextField('Group Name', validators=[DataRequired('Enter a group name')])
    edit_group_members = SelectMultipleField('Members', choices=[])


class EditScheme(Form):
    edit_scheme_id = HiddenField()
    edit_scheme_name = TextField('Scheme Name', validators=[DataRequired('Enter a name for this scheme of work')])
    edit_scheme_objectives = SelectMultipleField('Objectives', choices=[])


class SendMessage(Form):
    message_type = RadioField('Group or Individual Message',
                              choices=[('Individual', 'Individual'), ('Group', 'Group')],
                              default='Individual',
                              validators=[DataRequired(
                                  'Please specify whether you are sending an individual or a group message')])
    message_to = TextField('To', validators=[optional()])
    message_to_group = SelectField('To', choices=[], validators=[optional()])
    message_subject = TextField('Message Subject')
    message_body = TextAreaField('Message Content')
    recommended_material = SelectField('Recommend Material', choices=[])
    assign_objective = SelectField('Assign Objective', choices=[])
    assign_scheme = SelectField('Assign Scheme of Work', choices=[])
    request_access = BooleanField("Request to view students' progress", default=False)

    #def validate_message_to(self, field):
    #    if not User.user_by_email(field.data):
    #        raise ValidationError('This email address is not recognised')