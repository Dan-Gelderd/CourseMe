# -*- coding: utf-8 -*-
"""Service layer for Messages"""

from courseme.main.services.base import BaseService
from courseme.models import Message

import schema as s
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import load_only
from courseme.util import merge
from courseme import db

from courseme.errors import NotAuthorised, ValidationError

class MessageService(BaseService):
    __model__ = Message

    _base_schema = {
        'from_id': s.Use(int),
        'to_id'
        'subject': basestring,
        'recommended_material_id': s.Or(None, s.Use(int)),
        'assign_objective_id':s.Or(None, s.Use(int)),
        'assign_scheme_id':s.Or(None, s.Use(int))
    }

    def send(self, message_data, by_user):
        """Create a new Message from the given data

        :param message_data: is a dictionary of data used to populate the
                               initial Message.  It must match the schema
                               defined within.
        :param by_user: the `User` who is creating the `Message`.
        """

        creation_schema = self._base_schema

        m = s.Schema(creation_schema).validate(message_data)

        self._check_user_id(m['from_id'], by_user)
        #self._can_message(m['from_id'], m['to_id'])

        now = datetime.utcnow()
        m['sent'] = now

        message = Message(**m)
        db.session.add(message)
        db.session.commit()
        return message


    #from_id, to_id, subject, body, recommended_material_id, assign_objective_id, assign_scheme_id