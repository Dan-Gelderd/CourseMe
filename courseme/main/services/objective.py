# -*- coding: utf-8 -*-
"""Service layer for Objectives"""

import schema as s
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import load_only

from courseme import db
from courseme.models import Objective, User, UserObjective, SchemeOfWork
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

    def available_to(self, user, matching_names):
        """List of Objectives available to the given User

        :param user: User
        :param matching_names: list of Objective names to further
                               restrict availability.

        TODO: matching should probably match on ID, rather than name.  It's
              based on the name because that's what the form that ultimately
              uses this query is using, but that could be changed.
        """
        # DJG - Ian's sick querying skills
        # q = Objective.query.filter(
        #    and_(
        #        Objective.subject_id == user.subject_id,
        #        or_(
        #            Objective.created_by_id.in_(
        #                User.admin_usersQ().options(load_only("id"))),
        #            Objective.created_by_id == user.id)))

        q = self.objectives_for_selection(user, user.subject_id)
        if matching_names:
            # DJG - Avoid using in_ when list is empty as this is inefficient
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
            'subject_id': s.Or(None, s.Use(int)),
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
        :param by_user: the `User` who is updating the `Objective`.
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

        UserObjective.FindOrCreate(by_user.id, by_user.id, objective.id)
        # Adds a record to the UserObjective table if not already there. This is the official record of what objectives
        # should be visible to the user

        return objective


    def delete(self, objective_id, by_user):
        """Delete an objective.

        :param objective_id: is the id of the `Objective` to be deleted.
        :param by_user: the `User` who is deleting the `Objective`.
        """

        delete_schema = {'id': s.Use(int)}
        o = s.Schema(delete_schema).validate({'id': objective_id})
        # DJG - do I need to be using schema here. I just want to check the single id data item
        objective = self.require_by_id(o['id'])

        self._check_delete_auth(objective, by_user)
        db.session.delete(objective)
        db.session.commit()


    def remove(self, objective_id, student_id, tutor_id, by_user):
        """Remove an objective from a users set of adopted objectives.

        :param objective_id: is the id of the `Objective` to be removed.
        :param student_id: is the id of the `User` for whom the `Objective` is being removed.
        :param tutor_id: is the id of the `User` who is removing the `Objective`.
        :param by_user: is the `User` who is calling the action.
        """

        remove_schema = {'id': s.Use(int),
                         'student_id': s.Use(int),
                         'tutor_id': s.Use(int)
        }
        s.Schema(remove_schema).validate({'id': objective_id,
                                              'student_id': student_id,
                                              'tutor_id': tutor_id})

        self._check_user_id_or_admin(tutor_id, by_user)
        UserObjective.ignore_or_delete(student_id, tutor_id, objective_id)

        # DJG - how do students remove objectives? Is it related to tutor removing the objective for them? What if you add an objective in error.

    def find_or_include(self, objective_id, student_id, tutor_id, by_user, common_assessors=True):
        """Include an objective among a users set of adopted objectives.

        :param objective_id: is the id of the `Objective` to be included.
        :param student_id: is the id of the `User` for whom the `Objective` is being included.
        :param tutor_id: is the id of the `User` who is including the `Objective`.
        :param by_user: is the `User` who is calling the action.
        :param common_assessors: determines whether common assessors should have their assessment updated for the 'Student'.
        """

        include_schema = {'objective_id': s.Use(int),
                         'user_id': s.Use(int),
                         'assessor_id': s.Use(int)
        }
        u = s.Schema(include_schema).validate({'objective_id': objective_id,
                                              'user_id': student_id,
                                              'assessor_id': tutor_id})

        self._check_user_id_or_admin(u['assessor_id'], by_user)

        userobjective = UserObjective.query.filter_by(**u).first()

        if userobjective is None:
            userobjective = UserObjective.create(**u)
            # DJG - this includes a repetition of the logic to first search for a userobjective before creating it - is it better to have a fat model which listens for the new userobjective to be created and then acts on that
            if common_assessors:
                self._set_common_assessors(userobjective)
                self._set_student_objective(userobjective)

        return userobjective

    def objectives_for_selection(self, user, subject_id = None):
        """The set of 'Objectives' that are visible to the 'User' is the set of system objectives and the objectives the
        user has some self assessment for.

        :param user: is the 'User' for whom the objectives are being collected.
        :param subject_id: is the id of the `Subject` that will be used to filter the set of `Objectives` returned.
        """

        q = Objective.query.union(
                    Objective.system_objectives_q(subject_id),
                    Objective.assigned_objectives_q(user.id, user.id)
        )
        q = self._filter_on_subject(q, subject_id)
        return q

    def objectives_for_assessment(self, user, student_id, subject_id = None):
        """The set of 'Objectives' that are visible to the 'User' for the purpose of assessing a given student.

        :param user: is the 'User' for whom the objectives are being collected.
        :param student_id: is the id of the 'User' who is being assessed.
        :param subject_id: is the id of the `Subject` that will be used to filter the set of `Objectives` returned.
        """
        q = Objective.assigned_objectives_q(user.id, student_id)
        q = self._filter_on_subject(q, subject_id)
        return q

    def assess(self, objective_id, student_id, tutor_id, by_user):
        """Remove an objective from a users set of adopted objectives.

        :param objective_id: is the id of the `Objective` to be removed.
        :param student_id: is the id of the `User` for whom the `Objective` is being removed.
        :param tutor_id: is the id of the `User` who is removing the `Objective`.
        :param by_user: is the `User` who is removing the `Objective`.
        """

        assess_schema = {'student_id': s.Use(int),
                         'tutor_id': s.Use(int),
                         'objective_id': s.Use(int)
        }
        u = s.Schema(assess_schema).validate({'objective_id': objective_id,
                                            'student_id': student_id,
                                            'tutor_id': tutor_id})

        self._check_user_id(tutor_id, by_user)

        userobjective = self.find_or_include(by_user=by_user, common_assessors=True, **u)

        states = UserObjective.assessment_states().keys()
        completed = states[(states.index(userobjective.completed) + 1) % len(states)]  # Cycles through the list of states
        userobjective.completed = completed
        db.session.add(userobjective)
        db.session.commit()

        self._set_common_assessors(userobjective)
        self._set_student_objective(userobjective)
        return UserObjective.assessment_states()[completed]

    def schemes_for_selection(self, user, subject_id = None):
        """The set of 'Schemes of Work' that are visible to the 'User' is the set of schemes they have defined plus
        any others they are viewing.

        :param user: is the 'User' for whom the schemes are being collected.
        :param subject_id: is the id of the `Subject` that will be used to filter the set of `Schemes` returned.
        """

        q = SchemeOfWork.query.union(user.schemes_of_work_used, SchemeOfWork.query.filter(SchemeOfWork.creator_id==user.id))
        # DJG - build in filtering out any schemes with no objectives for selected subject
        return q.all()

        return []

    def _set_student_objective(self, userobjective):
        student_id = userobjective.user_id
        tutor_id = userobjective.assessor_id
        objective_id = userobjective.objective_id
        if User._is_authorised(student_id, tutor_id):
            self.find_or_include(objective_id=objective_id,
                                 student_id=student_id,
                                 tutor_id=student_id,
                                 by_user=User.main_admin_user(),
                                 common_assessors=False)

    def _set_common_assessors(self, userobjective):
        # Set all other members from the student's institution to have the same assessment. Assessment is therefore an institution wide thing bt stored at the individual member level
        student_id = userobjective.user_id
        tutor_id = userobjective.assessor_id
        objective_id = userobjective.objective_id
        print User._common_assessors(student_id, tutor_id)
        for member in User._common_assessors(student_id, tutor_id):
            userobj = self.find_or_include(objective_id=objective_id,
                                            student_id=student_id,
                                            tutor_id=member.id,
                                            by_user=User.main_admin_user(),
                                            common_assessors=False)
            userobj.completed = userobjective.completed
            db.session.add(userobj)
        db.session.commit()

    def _filter_on_subject(self, query, subject_id = None):
        if subject_id:
            return query.filter(Objective.subject_id == subject_id)
        else:
            return query

    def _check_update_auth(self, objective, user):
        if not user.is_admin():
            raise NotAuthorised

    def _check_delete_auth(self, objective, user):
        self._check_update_auth(objective, user)
        # DJG - initially assume delete authentication is same as update authentication
        # DJG - How do you just pass the arguments through without naming them if you know they are the same?

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
