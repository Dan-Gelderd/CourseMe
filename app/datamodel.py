#!/usr/bin/env python

from datetime import datetime
import json


class Module(object):
    _modules = {}                   # DJG - just for the static database - would change to a database lookup once we have mongodb
    
    def __init__(self, name):
        self.name = name
        
        self.objectives = set()
        self.author = None
        self.votes = 0            # DJG - Maybe keep here as shorthand for the vote count rather than do a sum over usermodules
        
        self.save()
        
    def save(self):
        self._modules[self.name] = self

        
    @classmethod
    def find(cls, name):            # DJG - just for the static database - would change to a database lookup once we have mongodb
        return cls._modules[name]

class User(object):
    _users = {}                     # DJG - just for the static database - would change to a database lookup once we have mongodb

    def __init__(self, name):
        self.name = name
        self.blurb = ""
        
        self.institutions = set()
        self.modules = set()        #DJG - don't understand these three
        self.courses = set()
        self.recommendations = set()

    def save(self):
        self._users[self.name] = self
        
    @classmethod
    def find(cls, name):            # DJG - just for the static database - would change to a database lookup once we have mongodb
        return cls._users[name]    

        
class Course(object):
    def __init__(self):
        self.name = "Course 1"

        self.author = None
        self.modules = []

class Objective(object):
    _objectives = {}                # DJG - just for the static database - would change to a database lookup once we have mongodb

    def __init__(self, name):
        self.name = name

        self.prerequisites = set()

        self.save()

    def save(self):
        self._objectives[self.name] = self
        
    @classmethod
    def find(cls, name):            # DJG - just for the static database - would change to a database lookup once we have mongodb
        return cls._objectives[name]
        
class Group(object):
    def __init__(self):
        self.name = "Group 1"
        
        self.creator = None
        self.members = set()

class Recommendation(object):
    def __init__(self):
        self.from_user = None
        self.to_user = None
        self.module = None

class UserModule(object):
    _usermodules = {}                   # DJG - just for the static database - would change to a database lookup once we have mongodb

    def __init__(self, user, module):
        self.initiated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.starred = False
        self.vote = 0
        self.notes = ""

        self.user = user
        self.module = module

        self.save()

    def save(self):
        self._usermodules[self.user, self.module] = self

    def as_json(self):
        data = {}
        data['user'] = self.user.name
        data['module'] = self.module.name
        data['starred'] = self.starred
        data['vote'] = self.vote
        return json.dumps(data, sort_keys=True, separators=(',',':'))

    @classmethod
    def find(cls, user, module):                # DJG - just for the static database - would change to a database lookup once we have mongodb
        return cls._usermodules[user, module]


class UserCourse(object):
    pass

class Institution(object):
    def __init__(self):
        self.name = "Institution 1"
        self.blurb = "This institution creates lots of great material"
        self.website = "www.Institution1.com"

        self.users = set()