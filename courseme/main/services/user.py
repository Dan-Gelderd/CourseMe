# -*- coding: utf-8 -*-
"""Service layer for Users"""

from courseme.main.services.base import BaseService
from courseme.models import User
from courseme.errors import NotFound, NotAuthorised

class UserService(BaseService):
    __model__ = User

