import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'courseme.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


UPLOADS_DEFAULT_DEST = os.path.join(basedir, 'uploads')      #DJG - This is a guess copied from above, what does it do?
UPLOADS_DEFAULT_URL = "/"

RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'