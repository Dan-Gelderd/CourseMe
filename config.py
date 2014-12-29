import os
basedir = os.path.abspath(os.path.dirname(__file__))



CSRF_ENABLED = True
SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'courseme-dev.db')

UPLOADS_DEFAULT_DEST = os.path.join(basedir, 'uploads')      #DJG - This is a guess copied from above, what does it do?
UPLOADS_DEFAULT_URL = "/"

RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'



