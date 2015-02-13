from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, TextAreaField, PasswordField, BooleanField, HiddenField, FileField, SelectMultipleField, \
    SelectField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, url


class CreateInstitution(Form):
    name = TextField('Name', validators=[DataRequired('You must enter a name for your institution')])
    license = TextField('License', validators=[
        DataRequired('Enter a recipient or group of recipients for your message'),
        Length(min=1, message='Institution name is too short'),
        Regexp('^[A-Za-z][A-Za-z0-9_.\- ]*$', 0, 'Institution names must have only letters, numbers, dots, dashes, underscores, or spaces')]
    )
