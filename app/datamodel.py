import datetime

class Module(object):
    _modules = {}           # DJG - just for the static database - would change to a database lookup once we have mongodb
    
    def __init__(self, name):
        self.name = name
        
        self.objectives = set()
        self.author = None
        #self.vote = 333
        
        self.save()
        
    def save(self):
        self._modules[self.name] = self
        
    @classmethod
    def find(cls, name):            # DJG - just for the static database - would change to a database ;lookup once we have mongodb
        return cls._modules[name]

        
    
class User(object):
    def __init__(self):
        self.name = "User 1"
        
        self.modules = set()
        self.courses = set()
        self.recommendations = set()
        
class Course(object):
    def __init__(self):
        self.name = "Course 1"

        self.author = None
        self.modules = []

class Objective(object):
    def __init__(self):
        self.name = "Objective 1"
        
        self.prerequisites = set()
        
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
    def __init__(self):
        self.completed = date(01/01/2014)
        self.starred = False

        self.user = None
        self.module = None

class UserCourse(object):
    pass

class Vote(object):
    def __init__(self):
        self.value = 0
        
        self.voter = None
        self.module = None
        
class Institution(object):
    def __init__(self):
        self.name = "Institution 1"
        self.blurb = "Institution 1"
        self.website = "Institution 1"

        self.users = set()