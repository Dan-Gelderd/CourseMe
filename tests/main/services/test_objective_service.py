# -*- coding: utf-8 -*-
import unittest

from courseme import create_app, db
from courseme.util import merge
from courseme.main.services import Services
from courseme.errors import ValidationError

class ObjectServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self._create_fixtures()
        self.services = Services()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_creates_objective_with_no_prerequisites(self):

        data = {
            'name': 'objective-1',
            'prerequisites': [],
            'topic_id': self.topic.id,
            'subject_id': self.subject.id
        }

        self.services.objectives.create(data, self.user)

    def test_creates_objective_with_prerequisites(self):

        base = {
            'topic_id': self.topic.id,
            'subject_id': self.subject.id,
            'prerequisites': []
        }

        def create_prereq(name):
            d = merge(base, { 'name': name })
            self.services.objectives.create(d, self.user)

        create_prereq('prereq-1')
        create_prereq('prereq-2')

        data = merge(base, {
            'prerequisites': ['prereq-1', 'prereq-2'],
            'name': 'test'
        })
        self.services.objectives.create(data, self.user)

    def test_not_possible_to_create_two_objectives_with_the_same_name(self):

        data = {
            'name': 'objective-1',
            'prerequisites': [],
            'topic_id': self.topic.id,
            'subject_id': self.subject.id
        }

        self.services.objectives.create(data, self.user)
        self.assertRaises(ValidationError,
                          self.services.objectives.create,
                          data, self.user)

    def _create_fixtures(self):
        # would probably be better that these are created through
        # the service layer as that mimics what the users of the
        # ObjectiveService would do.

        from courseme.models import User, Subject, Topic

        self.subject = Subject(name='Test Subject')
        self.user = User(name='Test User',
                         email='test@example.com',
                         password='secret',
                         subject=self.subject)
        self.topic = Topic(name='Test Topic',
                           subject=self.subject)
        db.session.add(self.subject)
        db.session.add(self.user)
        db.session.add(self.topic)
        db.session.commit()
