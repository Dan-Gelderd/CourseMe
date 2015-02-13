from flask import Blueprint

institutions = Blueprint('institutions', __name__)

from . import views