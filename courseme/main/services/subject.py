# -*- coding: utf-8 -*-
"""Service layer for Subjects"""

from courseme.main.services.base import BaseService
from courseme.models import Subject

class SubjectService(BaseService):
    __model__ = Subject

    def all(self):
        return Subject.query.all()