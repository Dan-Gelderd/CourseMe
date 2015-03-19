# -*- coding: utf-8 -*-
"""Service layer for Objectives"""

import schema as s
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import load_only

from courseme import db
from courseme.models import Objective, User
from courseme.main.services.base import BaseService
from courseme.util import merge
from courseme.errors import NotAuthorised, ValidationError

class ObjectiveService(BaseService):

    __model__ = Objective

    _base_schema = {
        'name': basestring,
        'prerequisites': [basestring],
        'topic_id': s.Or(None, s.Use(int)),
    }

    def by_name(self, name):
        """Lookup Objective by name.  Returns None if not found."""
        return Objective.query.filter(Objective.name == name).first()

    def available_to(self, user, matching_names=None):
        """List of Objectives available to the given User

        :param user: User
        :param matching_names: optional list of Objective names to further
                               restrict availability.

        TODO: matching should probably match on ID, rather than name.  It's
              based on the name because that's what the form that ultimately
              uses this query is using, but that could be changed.
        """
        q = Objective.query.filter(
           and_(
               Objective.subject_id == user.subject_id,
               or_(
                   Objective.created_by_id.in_(
                       User.admin_usersQ().options(load_only("id"))),
                   Objective.created_by_id == user.id)))

        if matching_names:
            q = q.filter(Objective.name.in_(matching_names))

        return q.all()

    def create(self, objective_data, by_user):
        """Create a new Objective from the given data

        :param objective_data: is a dictionary of data used to populate the
                               initial Objective.  It must match the schema
                               defined within.
        :param by_user: the `User` who is creating the `Objective`.
        """

        creation_schema = merge(self._base_schema, {
            s.Optional('id'): None,
            'subject_id': s.Use(int),
        })

        o = s.Schema(creation_schema).validate(objective_data)
        self._validate_topic(o['topic_id'], o['subject_id'])
        self._validate_name(o['name'])

        prerequisites = self._validate_prerequisites(o['prerequisites'], by_user)

        now = datetime.utcnow()
        o['prerequisites'] = prerequisites
        o['created_by_id'] = by_user.id
        o['last_updated'] = now
        o['time_created'] = now
        objective = Objective(**o)
        db.session.add(objective)
        db.session.commit()
        return objective


    def update(self, objective_data, by_user):
        """Update an existing Objective from the given data.

        :param objective_data: is a dictionary of data with the updated state
                               of the Objective.  It must match the schema
                               defined within.
        :param by_user: the `User` who is creating the `Objective`.
        """

        update_schema = merge(self._base_schema, {
            'id': s.Use(int),
        })

        o = s.Schema(update_schema).validate(objective_data)
        objective = self.require_by_id(o['id'])
        self._validate_topic(o['topic_id'], objective.subject_id)
        self._validate_name(o['name'], old_name=objective.name)

        prerequisites = self._validate_prerequisites(
                o['prerequisites'],
                by_user,
                check_cyclic_against=objective)

        self._check_update_auth(objective, by_user)
        
        now = datetime.utcnow()
        objective.last_updated = now
        objective.name = o['name']
        objective.prerequisites = prerequisites
        objective.topic_id = o['topic_id']
        db.session.add(objective)
        db.session.commit()
        return objective

    def _check_update_auth(self, objective, user):
        if not user.is_admin and objective.created_by_id != user.id:
            raise NotAuthorised

    def _validate_topic(self, topic_id, subject_id):
        t = self.services.topics.require_by_id(topic_id) if topic_id else None
        if t and t.subject_id != subject_id:
            raise ValidationError(
                topic_id="Topic's subject must match Objective's")

    def _validate_name(self, name, old_name=None):
        if name != old_name:
            if self.by_name(name):
                raise ValidationError(
                    name="Objective with this name already exists")

    def _validate_prerequisites(self, prereq_names, user, check_cyclic_against=None):

        if not prereq_names:
            return []

        available = self.available_to(user, matching_names=prereq_names)
        available_names = set([o.name for o in available])
        selected_names = set(prereq_names)

        if not selected_names <= available_names:
            diff = selected_names - available_names
            raise ValidationError(
                prerequisites=u"Given pre-requisites are not available: {}".format(
                    u', '.join(diff)))

        if check_cyclic_against:
            cycles = [p.name for p in available \
                            if p.is_required_indirect(check_cyclic_against)]
            if cycles:
                raise ValidationError(
                    prerequisites=u"Cyclic pre-requisites: {}".format(
                        u', '.join(cycles)))

        return available
