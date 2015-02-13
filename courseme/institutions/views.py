from flask import render_template, flash, redirect, session, url_for, request, g
from . import institutions
import forms
from .. models import User, ROLE_USER, ROLE_ADMIN, Institution
from .. email import send_email
import courseme.util.json as json

@institutions.route('/create-institution', methods=['GET, POST'])
def create_institution():
    title = "CourseMe - Institution"
    form = forms.CreateInstitution()
    return render_template('institutions/create_institution.html',
                           title=title,
                           form=form
    )
