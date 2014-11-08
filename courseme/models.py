#from flask import g         #DJG - Just added this to get the TopicChoices static method working. Could maybe otherwise add it as a method of User; doesn't work
from courseme import db
import json, operator
from datetime import datetime, timedelta
import md5
from sqlalchemy import desc

ROLE_USER = 0
ROLE_ADMIN = 1

VIEW_ALL = 0
VIEW_SYSTEM = 1
VIEW_OWN = 2

OBJ_NOT = 0
OBJ_PART = 1
OBJ_FULL = 2

ENTERPRISE_LICENCE_DURATION = 1


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), nullable=False, unique = True)    
    time_created = db.Column(db.DateTime)
    
    topics = db.relationship("Topic", backref="subject", lazy='dynamic')
    objectives = db.relationship("Objective", backref="subject", lazy='dynamic')
    modules = db.relationship("Module", primaryjoin="Module.subject_id==Subject.id", backref="subject", lazy='dynamic')
    questions = db.relationship("Question", backref="subject", lazy='dynamic')

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), nullable=False, unique = True)    
    time_created = db.Column(db.DateTime)
    subject_id = db.Column(db.Integer, db.ForeignKey(Subject.id), nullable=False)     

    objectives = db.relationship("Objective", backref="topic", lazy='dynamic')    

    @staticmethod
    def TopicChoices(user):
        return [(str(topic.id), topic.name) for topic in Topic.query.filter(Topic.subject_id == user.subject_id).all()]


student_tutor = db.Table("student_tutor",
    db.Column("tutor_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("student_id", db.Integer, db.ForeignKey("user.id"))
)

question_selections = db.Table('question_selections',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.String(120), nullable=False)      #DJG - What does index=True do?
    email = db.Column(db.String(120), index = True, unique = True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    blurb = db.Column(db.String(240), default = "This is some blurb")
    role = db.Column(db.SmallInteger, default = ROLE_USER, nullable=False)
    last_seen =  db.Column(db.DateTime)
    time_registered = db.Column(db.DateTime)
    enterprise_licence = db.Column(db.DateTime)
    view_system_only = db.Column(db.Boolean, default = False)  
    time_deleted = db.Column(db.DateTime)

    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))          
    subject = db.relationship("Subject")
    
    view_institution_only_id = db.Column(db.Integer, db.ForeignKey('institution.id'))           
    institution_student_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    
    view_institution_only = db.relationship("Institution", primaryjoin="Institution.id==User.view_institution_only_id", backref="users_viewing_approved")
    objectives_created = db.relationship("Objective", backref="created_by", lazy='dynamic')
    modules_authored = db.relationship("Module", backref="author", lazy = 'dynamic')
    questions_authored = db.relationship("Question", backref="author", lazy = 'dynamic')
    institutions_created = db.relationship("Institution", primaryjoin="Institution.creator_id==User.id", backref="creator", lazy='dynamic')
    groups_created = db.relationship("Group", primaryjoin="Group.creator_id==User.id", backref="creator", lazy='dynamic')
    schemes_of_work = db.relationship("SchemeOfWork", backref="creator", lazy='dynamic')

    students = db.relationship("User",
                    secondary=student_tutor,
                    primaryjoin=(student_tutor.c.tutor_id==id),
                    secondaryjoin=(student_tutor.c.student_id==id),
                    backref = db.backref('tutors', lazy = 'dynamic'),           #DJG - Does this need to be included to make the secondary table update when an objective is passed to session.delete()? 
                    lazy = 'dynamic',                                           #DJG - not the default, don't know why I need it: the attribute will return a pre-configured Query object for all read operations, onto which further filtering operations can be applied before iterating the results.
                    passive_updates=False)  

    questions_selected = db.relationship('Question', secondary=question_selections, lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)
    
    def avatar(self, size=50):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    def is_enterprise_licenced(self):
        if self:
            if self.role == ROLE_ADMIN:
                return True
            if self.enterprise_licence:
                licence_expiry_date = self.enterprise_licence + timedelta(years = ENTERPRISE_LICENCE_DURATION)
                if datetime.utcnow() <= licence_expiry_date :
                    return True
                else:
                    Message.AdminMessage(
                        to_id = self.id,
                        subject = "Enterprise Licence Expired",
                        body = "You have tried to perform an action requiring an enterprise licence. Your licence expired on " + licence_expiry_date + ". To renew your licence contact CourseMe at " + User.main_admin_user().email
                    )
                    return False
            else:
                Message.AdminMessage(
                    to_id = self.id,
                    subject = "Enterprise Licence Needed",
                    body = "You have tried to perform an action requiring an enterprise licence. To purchase a licence contact CourseMe at " + User.main_admin_user().email
                    )
                return False                

    def visible_objectives(self):
        visible_objective_user_ids = [u.id for u in User.admin_users()]
        visible_objective_user_ids.append(self.id)
        return Objective.query.filter(Objective.created_by_id.in_(visible_objective_user_ids)).filter(Objective.subject_id == self.subject_id)      #DJG - what about visible courses?

    def visible_questions(self):
        if self.subject_id > 0 :
            return Question.query.filter(Question.subject_id == self.subject_id)
        else:
            return Question.query


    def live_modules_authored(self):
        return Module.LiveModules().filter_by(author_id = self.id)

    def live_modules_authored_by_type(self, type):
        return self.live_modules_authored().filter_by(material_type = type)

    def live_modules_viewed(self):
        #return Module.LiveModules().filter(Module.id.in_(UserModule.query.filter_by(user=self).all()))
        return Module.LiveModules().join(UserModule).filter(UserModule.user == self)    

    def visible_modules(self):
        #import pdb; pdb.set_trace()            #DJG - remove
        query_authored_modules = self.live_modules_authored()
        query_viewed_modules = self.live_modules_viewed()
        institution_student = self.institution_student
        query_student_modules = Module.LiveModules()
        if institution_student:
            if institution_student.view_institution_only:
                query_student_modules = institution_student.view_institution_only.approved_modules
        if self.view_institution_only:
            query_select_modules = self.view_institution_only.approved_modules
        else:
            query_select_modules = Module.LiveModules()
        query_approved_modules = query_select_modules.intersect(query_student_modules)
        
        return query_approved_modules.union(query_authored_modules, query_viewed_modules)
        
    def enrolled_courses(self):
        #return [Module.query.get(um.module_id) for um in UserModule.query.filter_by(user=self).filter(UserModule.enrolled).order_by(desc(UserModule.last_viewed)).all()]        #DJG - can we do better with filter on boolean type?
        return self.live_modules_viewed().filter(UserModule.enrolled).filter(Module.material_type=='Course').order_by(desc(UserModule.last_viewed))
    
    def recent_modules(self, count):
        #import pdb; pdb.set_trace()        #DJG - remove
        if self:
            #return self.live_modules_viewed().order_by(desc(UserModule.last_viewed)).limit(count).all()     #DJG - working but not on index page
            return []
        else:
            return []
    
    def relevant_institutions(self):
        #DJG - must be able to do better than this!
        relevant_institutions = [Institution.main_courseme_institution()]
        relevant_institutions.extend(self.institutions_created.all())
        relevant_institutions.extend(self.institutions_member.all())
        if self.institution_student: relevant_institutions.append(self.institution_student)
        relevant_institutions = list(set(relevant_institutions))
        print relevant_institutions         #DJG - remove this
        return relevant_institutions
    
    def live_messages(self):
        return self.received_messages.filter(bool(Message.deleted)).order_by(desc(Message.sent))

    def institution_tutors(self):       #DJG - not really needed as a separate method means as creator is always added to list of members when institution created by create method
        return self.institution_student.members

    def permission(self, viewer):
        return self == viewer or viewer in self.tutors.all() or (self.institution_student and viewer in self.institution_tutors().all())
    
    def all_students(self):
        all_students = self.students.all()
        for i in self.institutions_member:
            all_students.extend(i.students.all())
        #import pdb; pdb.set_trace()
        return all_students    
    
    def has_students(self):         #DJG - change to use all students
        if self:
            has_students = bool(self.students.first())
            for i in self.institutions_member:
                has_students = has_students or bool(i.students.first())
            return has_students
        else:
            return False
    
    def allow_access(self, tutor):
        if not self.permission(tutor):
            self.tutors.append(tutor)
            db.session.add(self)
            db.session.commit()
            student_message = Message.AdminMessage(
                to_id = self.id,
                subject = "Access granted to new tutor - " + tutor.name,
                body = "You have granted permission to " + tutor.name + " to view your progress through learning objectives. You can review and change who has permission to view this information on your own profile page."        
            )
            Message.AdminMessage(
                to_id = tutor.id,
                subject = "Access granted to new student - " + self.name,
                body = "You have been granted permission by " + self.name + " to view their progress through learning objectives. You can view the learning objectives of you students on ...DJG - finish message."        
            )
            return True
        else:
            return False

    def deny_access(self, tutor):
        if self.permission(tutor):
            self.tutors.remove(tutor)
            db.session.add(self)
            db.session.commit()
            return True
        else:
            return False
        
    def question_selected(self, question):
        return question in self.questions_selected.all()
    
    def select_question(self, question):
        if not self.question_selected(question):
            self.questions_selected.append(question)
            db.session.commit()

    def deselect_question(self, question):
        if self.question_selected(question):
            self.questions_selected.remove(question)
            db.session.commit()

    def toggle_select_question(self, question):
        if self.question_selected(question):
            self.deselect_question(question)
            return ""
        else:
            self.select_question(question)
            return "success"        
        
    @staticmethod
    def make_unique_username(username):
        if User.query.filter_by(name = username).first() == None:
            return username
        version = 2
        while True:
            new_username = username + str(version)
            if User.query.filter_by(name = new_username).first() == None:
                break
            version += 1
        return new_username

    @staticmethod       #DJG - suspect this should be taken out of the user class as the user is passed to the template and so the server side through g.user - may therefore give access to the client about admin users?
    def admin_users():
        return User.query.filter(User.role == ROLE_ADMIN).all()

    @staticmethod 
    def main_admin_user():
        return User.query.get(1)
        #DJG - Not robust. Need some way to return the main system admin user

    @staticmethod
    def user_by_email(email):
        user = User.query.filter_by(email = email).first()      #DJG - want to use one to check for duplicates
        if user:
            return user
        else:
            return None

objective_heirarchy = db.Table("objective_heirarchy",
    db.Column("prerequisite_id", db.Integer, db.ForeignKey("objective.id")),
    db.Column("followon_id", db.Integer, db.ForeignKey("objective.id"))
)

class Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique = True, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey(Subject.id), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey(Topic.id))                               #DJG - need to change to reference to topic table
    description = db.Column(db.String(50), nullable=True)
    time_created = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)    
    assessable = db.Column(db.Boolean, nullable=False, default=True)

    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))     #DJG - why is user lower case in ForeignKey('user.id')    

    prerequisites = db.relationship("Objective",
                        secondary=objective_heirarchy,
                        primaryjoin=(objective_heirarchy.c.followon_id==id),
                        secondaryjoin=(objective_heirarchy.c.prerequisite_id==id),
                        backref = db.backref('followons', lazy = 'dynamic'),        #DJG - Does this need to be included to make the secondary table update when an objective is passed to session.delete()? 
                        lazy = 'dynamic',                                           #DJG - not the default, don't know why I need it: the attribute will return a pre-configured Query object for all read operations, onto which further filtering operations can be applied before iterating the results.
                        passive_updates=False)                                      #DJG - Does this need to be included to make the secondary table update when an objective is passed to session.delete()? 
    
    def require(self, objective):
        if not self.is_required(objective):
            self.prerequisites.append(objective)
            return self

    def unrequire(self, objective):
        if self.is_required(objective):
            self.prerequisites.remove(objective)
            return self

    def is_required_direct(self, objective):
        return self == objective or self.prerequisites.filter(objective_heirarchy.c.prerequisite_id == objective.id).count() > 0

    def is_required_indirect(self, objective):
        return self == objective or objective in self.all_prerequisites()

    def score(self):
        prerequisites = self.prerequisites.all()
        if prerequisites:
            return max(p.score() for p in prerequisites)+1
        else:
            return 1
    
    def all_prerequisites(self):
        all_prerequisites = set()
        prerequisites_found = set(self.prerequisites.all())
        while prerequisites_found:
            all_prerequisites = set.union(all_prerequisites, prerequisites_found)
            prerequisites_found_iterator = (set(p.prerequisites) for p in prerequisites_found)
            prerequisites_found = set.union(*prerequisites_found_iterator)          #DJG - http://stackoverflow.com/questions/14720436/set-union-complains-that-it-has-no-argument-when-passing-in-a-generator
        return list(all_prerequisites)
   
    def as_dict(self):
        #wouldn't handle relationships
        #public_fields = ['name']
        #return {key: getattr(self, key) for key in public_fields}  
        
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['subject'] = self.subject.name
        data['topic_id'] = self.topic_id        
        data['prerequisites'] = [p.name for p in self.prerequisites.all()]
        #return json.dumps(data, sort_keys=True, separators=(',',':'))      DJG - could convert to JSON in here
        return data

    def top_modules(self, exclude=None, material_type="Lecture", num=3):
        modules = self.modules.filter_by(material_type=material_type).order_by(Module.votes).limit(num+1).all()  #DJG - lookup modules for given objective sorted by votes of given type
        if exclude and exclude in modules: modules.remove(exclude)
        return modules[:num]
    
    def assessment(self, user, assessor):
        return UserObjective.query.filter_by(user_id=user.id, assessor_id=assessor.id, objective_id=self.id).first()

    def assessed(self, user, assessor):     #DJG - could probably do in one line
        userobjective = self.assessment(user, assessor)
        if userobjective:
            return userobjective.completed
        else:
            return 0

    def assessed_display_class(self, user, assessor):
        userobjective = self.assessment(user, assessor)
        if userobjective:
            return userobjective.assessed_display_class()
        else:
            return False
        
    @staticmethod
    def system_objectives():
        system_objectives_iterator = (set(u.objectives_created) for u in User.admin_users())
        system_objectives = set.union(*system_objectives_iterator)
        return system_objectives
    
    @staticmethod
    def Choices():
        try:        #DJG - this exception handling is needed because the forms module references this method and so on database creation it creates an error since the table cannot be found and queries. Perhaps there is a better way to prevent the cyclic dependency on startup
            return [(str(objective.id), objective.name) for objective in Objective.query.all()]
        except:
            return []

module_objectives = db.Table('module_objectives',
    db.Column('module_id', db.Integer, db.ForeignKey('module.id')),
    db.Column('objective_id', db.Integer, db.ForeignKey('objective.id'))
)

course_modules = db.Table('course_modules',
    db.Column('course_id', db.Integer, db.ForeignKey('module.id')),
    db.Column('module_id', db.Integer, db.ForeignKey('module.id'))
)


scheme_objectives = db.Table('scheme_objectives',
    db.Column('scheme_id', db.Integer, db.ForeignKey('scheme_of_work.id')),
    db.Column('objective_id', db.Integer, db.ForeignKey('objective.id'))
)

class SchemeOfWork(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))    
    creator_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)        #DJG - need , use_alter=True, name='fk_institution_creator_id' to avoid circular join references

    objectives = db.relationship(Objective, secondary=scheme_objectives, lazy='dynamic',
        backref=db.backref('schemes_of_work', lazy='dynamic'))
    
    def is_objective(self, objective):
        return self.objectives.filter(scheme_objectives.c.objective_id == objective.id).count() > 0

    def add_objective(self, objective):
        if user:
            if not self.is_objective(objective):
                self.objectives.append(objective)
                db.session.add(self)
                db.session.commit()
        else:
            pass
        
    def as_dict(self):
        result = {}
        result['id'] = self.id
        result['name'] = self.name
        result['objectives'] = [objective.name for objective in self.objectives]
        return result

class UserObjective(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    assessor_id = db.Column(db.Integer, db.ForeignKey(User.id))
    objective_id = db.Column(db.Integer, db.ForeignKey(Objective.id))
    completed = db.Column(db.SmallInteger, default = OBJ_NOT)

    user = db.relationship(User, primaryjoin="User.id==UserObjective.user_id", backref='user_objectives')
    assessor = db.relationship(User, primaryjoin="User.id==UserObjective.assessor_id", backref='assessed_objectives')
    objective = db.relationship(Objective, backref='user_objectives')
    
    
    def assess(self):
        states = (OBJ_NOT, OBJ_PART, OBJ_FULL)
        completed = states[(states.index(self.completed)+1) % len(states)]      #Cycles through the list of states
        print completed
        self.completed = completed
        db.session.add(self)
        #Set all other members from the student's institution to have the same assessment. Assessment is therefore an institution wide thing bt stored at the individual member level
        institution = self.user.institution_student
        if institution:
            if institution.is_member(self.assessor):
                for member in institution.members:
                    userobjective = UserObjective.FindOrCreate(user_id=self.user_id, assessor_id=member.id, objective_id=self.objective_id)
                    userobjective.completed = completed
                    db.session.add(userobjective)
        db.session.commit()
    
    def assessed_display_class(self):
        display_classes = {
            OBJ_NOT: "objective_not",
            OBJ_PART: "objective_partial warning",
            OBJ_FULL: "objective_complete success"
        }
        return display_classes[self.completed]
    
    @staticmethod
    def FindOrCreate(user_id, assessor_id, objective_id):
        #DJG - should check for multiple query returns
        userobjective = UserObjective.query.filter_by(user_id=user_id, assessor_id=assessor_id, objective_id=objective_id).first()
        if userobjective is None:
            userobjective = UserObjective(
                user_id=user_id,
                assessor_id=assessor_id,
                objective_id=objective_id
                )
            db.session.add(userobjective)
            db.session.commit()
        return userobjective
    
class Module(db.Model):                                             #DJG - change this class to material as it now captures modules and courses
    id = db.Column(db.Integer, primary_key = True)      
    name = db.Column(db.String(120))
    description = db.Column(db.String(400))
    notes = db.Column(db.String(400))
    material_type = db.Column(db.String(120), default = 'Lecture')
    time_created = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
    material_source = db.Column(db.String(120), default = 'youtube')
    material_path = db.Column(db.String(400))
    submitted = db.Column(db.DateTime) 
    published = db.Column(db.DateTime)
    locked = db.Column(db.DateTime)
    deleted = db.Column(db.DateTime)
    live = db.Column(db.Boolean, default = True)
    subtitles = db.Column(db.Boolean, default = False)
    easy_language = db.Column(db.Boolean, default = False)
    extension = db.Column(db.Boolean, default = False)
    for_teachers = db.Column(db.Boolean, default = False)
    visually_impaired = db.Column(db.Boolean, default = False)
    votes = db.Column(db.Integer, default = 0)

    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable = False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)     #DJG - why is user lower case in ForeignKey('user.id')

    objectives = db.relationship('Objective', secondary=module_objectives,      #DJG - shouldn't I have lazy = dynamic here too?
        backref=db.backref('modules', lazy='dynamic'))

    modules = db.relationship("Module",
                        secondary=course_modules,
                        primaryjoin=(course_modules.c.course_id==id),
                        secondaryjoin=(course_modules.c.module_id==id),
                        backref = db.backref('courses', lazy = 'dynamic'),        #DJG - Does this need to be included to make the secondary table update when an objective is passed to session.delete()? 
                        lazy = 'dynamic',                                       
                        passive_updates=False)

    #def subject_id(self):
    #    return self.objectives[0].subject_id

    def calculate_votes():
        pass #DJG - calculate the proper votes total by summing usermodules and store in this parameter, to be run periodically to keep votes count properly alligned; should print out a record if mismatched to developer log

    def icon_class(self):
        icon_classes = {"Course": "glyphicon glyphicon-list-alt",
                        "Lecture": "glyphicon glyphicon-play-circle",
                        "Exercise": "glyphicon glyphicon-check",
                        "Tool": "glyphicon glyphicon-wrench"
                        }
        return icon_classes[self.material_type]

    def is_courseable(self):
        return self.material_type != "Course"

    def delete(self, alternative=0):
        self.deleted = datetime.utcnow()
        self.live = False
        for course in self.courses.all():
            course.modules.remove(self)
        for um in self.user_modules:
            um.delete(alternative)
        db.session.commit()

    def course_objectives(self):
        if self.material_type == "Course":
            course_objectives = [obj for mod in self.modules for obj in mod.objectives]
            course_objectives = list(set(course_objectives))
            course_objectives.sort(key=operator.methodcaller("score"))
            return course_objectives
        else:
            return self.objectives

    def as_dict(self):
        result = self.__dict__
        result['author'] = self.author.name
        result['objectives'] = [o.name for o in self.objectives]
        del result['_sa_instance_state']
        return result

    def add_to_author_institutions(self):
        for i in self.author.institutions:
            i.approved_modules = i.approved_modules.append(self)
        
    @staticmethod
    def LiveModules():
        return Module.query.filter(Module.live)

    @staticmethod
    def RecommendChoices():
        try:        #DJG - this exception handling is needed because the forms module references this method and so on database creation it creates an error since the table cannot be found and queries. Perhaps there is a better way to prevent the cyclic dependency on startup
            return [(str(module.id), module.name) for module in Module.LiveModules().all()]
        except:
            return []
    
class UserModule(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    module_id = db.Column(db.Integer, db.ForeignKey(Module.id))
    first_viewed = db.Column(db.DateTime)
    last_viewed = db.Column(db.DateTime)
    starred = db.Column(db.Boolean, default = False)
    vote = db.Column(db.Integer, default = 0)
    notes = db.Column(db.String(1000))
    enrolled = db.Column(db.Boolean, default = False)
    deleted = db.Column(db.Boolean, default = False)

    user = db.relationship(User, backref='user_modules')
    module = db.relationship(Module, backref='user_modules')
    
    
    def part_of_course(self, relevance="enrolled"):
        courses = []
        if relevance == "enrolled":
            courses = self.user.enrolled_courses().all()
        elif relevance == "authored":
            courses = self.user.modules_authored.all()
        for course in courses:
            if course.material_type=="Course":
                if self.module in course.modules:
                    return course
        return None

    def completed(self):
        #import pdb; pdb.set_trace()
        if self:
            if self.module.material_type != "Course":
                return 1                #DJG - need some better logic here about whether a lecture or exercise has been completed
            else:
                course_module_ids = [mod.id for mod in self.module.modules]
                course_length = len(course_module_ids)
                return sum(um.completed() for um in UserModule.query.filter_by(user_id=self.user.id).filter(UserModule.module_id.in_(course_module_ids)).all())/course_length
        else:
            return 0

    def course_completed(self):
        course = self.part_of_course()
        if course:    
            user_course = UserModule.query.filter_by(user_id=self.user.id, module_id=course.id).one()
            return user_course.completed()
        else:
            return 0 

    def important(self, recent=7):
        message = ""
        material_type = self.module.material_type
        authored_course = self.part_of_course("authored")
        if authored_course: return material_type + " you are using in your Course '" + authored_course.name + "'"
        if self.enrolled: return material_type + " you have enrolled in"
        if self.part_of_course(): return material_type + " within a Course you have enrolled in"
        if self.starred: return "Starred " + material_type  
        if self.last_viewed >= datetime.now()-timedelta(days = recent): return "recently viewed " + material_type

    
    def delete(self, alternative=0):
        self.deleted = True
        important = self.important()
        if important:
            body="A " + important + ", " + self.module.name + ", has been deleted."
            if alternative: pass
            Message.AdminMessage(to_id=self.user.id,
                                 subject="Material Deleted",
                                 body=body,
                                 recommended_material_id=alternative)
        db.session.commit()
    
    def as_json(self):
        data = {}
        data['id'] = self.id
        data['starred'] = self.starred
        data['vote'] = self.vote
        return json.dumps(data, sort_keys=True, separators=(',',':'))
    

    @staticmethod
    def FindOrCreate(user_id, module_id):
        usermodule = UserModule.query.filter_by(user_id=user_id, module_id=module_id).first()
        if usermodule is None:
            usermodule = UserModule(user_id=user_id,
                                    module_id=module_id,
                                    first_viewed=datetime.utcnow())
            #print "usermodule " + str(usermodule.id) + " created"       #DJG - delete
        else:
            pass    #print "usermodule " + str(usermodule.id) + " found"         #DJG - delete
        usermodule.last_viewed=datetime.utcnow()
        db.session.add(usermodule)
        db.session.commit()
        return usermodule


class Message(db.Model):     #DJG - probably need a separate one for module and course recommendations, need to add the relationship to the material being recommended and all the permissions
    id = db.Column(db.Integer, primary_key = True)
    from_id = db.Column(db.Integer, db.ForeignKey(User.id))
    to_id = db.Column(db.Integer, db.ForeignKey(User.id))
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=True)
    sent = db.Column(db.DateTime)
    read = db.Column(db.DateTime)
    reported = db.Column(db.DateTime)
    deleted = db.Column(db.DateTime)
    request_access = db.Column(db.Boolean, default = False)
    
    recommended_material_id = db.Column(db.Integer, db.ForeignKey(Module.id))   

    from_user = db.relationship(User, foreign_keys=[from_id], backref=db.backref('sent_messages', lazy="dynamic"))
    to_user = db.relationship(User, foreign_keys=[to_id], backref=db.backref('received_messages', lazy="dynamic"))
    recommended_material = db.relationship(Module, foreign_keys=[recommended_material_id], backref='recommendations')
    
    def report(self):
        self.reported = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
        #DJG - do some kind of notification process
    
    @staticmethod
    def AdminMessage(to_id, subject, body="", recommended_material_id=0):
        admin_message = Message(from_id=User.main_admin_user().id,
                to_id=to_id,
                subject=subject,
                body=body,
                sent=datetime.utcnow(),
                recommended_material_id=recommended_material_id)
        db.session.add(admin_message)
        db.session.commit()



group_members = db.Table('group_members',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('user.id'))
)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))    
    creator_id = db.Column(db.Integer, db.ForeignKey(User.id, use_alter=True, name='fk_group_creator_id'), nullable=False)        #DJG - need , use_alter=True, name='fk_institution_creator_id' to avoid circular join references

    members = db.relationship(User, secondary=group_members, lazy='dynamic',
        backref=db.backref('groups_member', lazy='dynamic'))
    
    def is_member(self, user):
        return self.members.filter(group_members.c.member_id == user.id).count() > 0

    def add_member(self, user):
        if user:
            if not self.is_member(user):
                self.members.append(user)
                #DJG - May not need to inform users if they are added to a group - purely an organisational tool for people to send messages and track proress
                #message = Message(
                #    from_id = self.creator_id,
                #    to_id = user.id,
                #    subject = "You have been added to the group " + self.name,
                #    body = "You have been added to the group " + self.name + ". If you want to leave this group go to the groups section of your profile page and click the button to leave.",
                #    sent = datetime.utcnow())
                #db.session.add(message)            
                db.session.add(self)
                db.session.commit()
        else:
            pass

    def message(self, subject, body, recommended_material=None, request_access=False):          #DJG - am I using this?
        for member in self.members:
            message = Message(
                from_id = self.creator_id,
                to_id = member.id,
                subject = subject,            
                body = body,
                sent=datetime.utcnow()
                )
            if recommended_material: message.recommended_material=recommended_material
            if request_access: message.request_access=request_access
            db.session.add(message)
            db.session.commit()

    def viewable_members(self):
        students = self.members.order_by(User.email).all()
        return [s for s in students if s in self.creator.all_students()]


    def as_dict(self):
        result = {}
        result['id'] = self.id
        result['name'] = self.name
        result['members'] = [user.email for user in self.members]
        return result

institution_members = db.Table('institution_members',
    db.Column('institution_id', db.Integer, db.ForeignKey('institution.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('user.id'))
)

institution_approved_modules = db.Table('institution_approved_modules',
    db.Column('institution_id', db.Integer, db.ForeignKey('institution.id')),
    db.Column('module_id', db.Integer, db.ForeignKey('module.id'))
)

class Institution(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), index = True, unique = True, nullable=False)    
    creator_id = db.Column(db.Integer, db.ForeignKey(User.id, use_alter=True, name='fk_institution_creator_id'), nullable=False)        #DJG - need , use_alter=True, name='fk_institution_creator_id' to avoid circular join references
    #generic_user_id = db.Column(db.Integer, db.ForeignKey(User.id, use_alter=True, name='fk_institution_creator_id'), nullable=False)        #DJG - need , use_alter=True, name='fk_institution_creator_id' to avoid circular join references    
    blurb = db.Column(db.String(400), default = "This is some blurb")    
    view_institution_only_id = db.Column(db.Integer, db.ForeignKey('institution.id'))    

    #generic_user = db.relationship(User, primaryjoin="Institution.generic_user_id==User.id", backref=db.backref("institution_generic", uselist=False))
    view_institution_only = db.relationship("Institution", remote_side=[id], backref="institutions_viewing_approved")

    members = db.relationship(User, secondary=institution_members, lazy='dynamic',
        backref=db.backref('institutions_member', lazy='dynamic'))
    
    students = db.relationship(User, primaryjoin="Institution.id==User.institution_student_id", backref="institution_student", lazy = 'dynamic')
    
    approved_modules = db.relationship('Module', secondary=institution_approved_modules, backref='approving_institutions', lazy = 'dynamic')

    def is_member(self, user):
        return self.members.filter(institution_members.c.member_id == user.id).count() > 0

    def is_student(self, user):         #DJG - think there is an exist query that checks for existence
        return self.students.filter(User.id == user.id).count() > 0    
    
    def is_approved(self, module):
        return self.approved_modules.filter(institution_approved_modules.c.module_id == module.id).count() > 0

    def add_member(self, user):
        if user:
            if not self.is_member(user):
                self.members.append(user)
                message = Message(
                    from_id = self.creator_id,
                    to_id = user.id,
                    subject = "You have been added to the institution " + self.name,
                    body = "You have been added to the institution " + self.name + ". All of your authored material will now appear on the approved list of modules for this institution and you can view the progress of all students of " + self.name + ". Your name will be listed on the institution profile page. If you want to leave this institution go to the institutions section of your profile page and click the button to leave.",
                    sent = datetime.utcnow())
                db.session.add(message)            
            for module in user.live_modules_authored().all():
                if not self.is_approved(module):
                    self.approved_modules.append(module)
            db.session.add(self)
            db.session.commit()
        else:
            pass

    def add_student(self, user, send_message=True):
        if user:
            if not self.is_student(user):
                self.students.append(user)
                if send_message:
                    message = Message.AdminMessage(
                        to_id = self.creator_id,
                        subject = "New student - " + user.name + " - added to institution " + self.name,
                        body = "A new student, " + user.name + ", has been added to your institution " + self.name + ". You can review the student list and remove students on the institution profile page."
                        )           
                db.session.add(self)
                db.session.commit()
        else:
            pass

    @staticmethod 
    def main_courseme_institution():
        return Institution.query.get(1)
        #DJG - Not robust. Need some way to return the main system institution
    
    @staticmethod     
    def create(name, creator, blurb=""):
        if Institution.query.filter_by(name=name).first():
            return False
        else:
            institution = Institution(
                name = name,
                creator_id = creator.id,    
                blurb = blurb,
                members = [creator]
                )
            db.session.add(institution)
            db.session.commit()
            return institution
        
question_objectives = db.Table('question_objectives',
    db.Column('question_id', db.Integer, db.ForeignKey('question.id')),
    db.Column('objective_id', db.Integer, db.ForeignKey('objective.id'))
)
        
class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True)      
    question = db.Column(db.String(5000))
    answer = db.Column(db.String(5000))
    time_created = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
    submitted = db.Column(db.DateTime) 
    published = db.Column(db.DateTime)
    locked = db.Column(db.DateTime)
    extension = db.Column(db.Boolean, default = False)
    visually_impaired = db.Column(db.Boolean, default = False)      #DJG - need to put this in forms and stuff
    votes = db.Column(db.Integer, default = 0)

    subject_id = db.Column(db.Integer, db.ForeignKey(Subject.id), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    objectives = db.relationship('Objective', secondary=question_objectives,   #DJG - shouldn't I have  lazy='dynamic', here too?
        backref=db.backref('questions', lazy='dynamic'))

    def as_dict(self):
        result = self.__dict__
        result['author'] = self.author.name
        result['objectives'] = [o.name for o in self.objectives]
        del result['_sa_instance_state']
        return result
   