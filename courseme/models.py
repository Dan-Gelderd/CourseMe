from courseme import db
import json
from datetime import datetime
import md5

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.String(120), index = True, nullable=False)      #DJG - What does index=True do?
    email = db.Column(db.String(120), index = True, unique = True, nullable=False)
    name = db.Column(db.String(64), index = True, nullable=False)
    blurb = db.Column(db.String(240), default = "This is some blurb")
    role = db.Column(db.SmallInteger, default = ROLE_USER, nullable=False)
    last_seen =  db.Column(db.DateTime)
    time_registered = db.Column(db.DateTime)

    objectives_created = db.relationship("Objective", backref="created_by")
    modules_authored = db.relationship("Module", backref="author")

    def visible_objectives(self):
        visible_objective_user_ids = [u.id for u in User.admin_users()]
        visible_objective_user_ids.append(self.id)
        return Objective.query.filter(Objective.created_by_id.in_(visible_objective_user_ids))   
        
    
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

    @staticmethod
    def admin_users():
        return User.query.filter(User.role == ROLE_ADMIN).all()

objective_heirarchy = db.Table("objective_heirarchy",
    db.Column("prerequisite_id", db.Integer, db.ForeignKey("objective.id")),
    db.Column("followon_id", db.Integer, db.ForeignKey("objective.id"))
)

class Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

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
        data['prerequisites'] = [p.name for p in self.prerequisites.all()]
        #return json.dumps(data, sort_keys=True, separators=(',',':'))      DJG - could convert to JSON in here
        return data

    @staticmethod
    def system_objectives():
        system_objectives_iterator = (set(u.objectives_created) for u in User.admin_users())
        system_objectives = set.union(*system_objectives_iterator)
        return system_objectives
    
    
class Module(db.Model):
    id = db.Column(db.Integer, primary_key = True)      
    name = db.Column(db.String(120))
    time_created = db.Column(db.DateTime)
    material_path = db.Column(db.String(400))
    votes = db.Column(db.Integer, default = 0)
    
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))     #DJG - why is user lower case in ForeignKey('user.id')
    
    def calculate_votes():
        pass #DJG - calculate the proper votes total by summing usermodules and store in this parameter, to be run periodically to keep votes count properly alligned; should print out a record if mismatched to developer log
    
class UserModule(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    module_id = db.Column(db.Integer, db.ForeignKey(Module.id))
    first_viewed = db.Column(db.DateTime)
    last_viewed = db.Column(db.DateTime)
    starred = db.Column(db.Boolean, default = False)
    vote = db.Column(db.Integer, default = 0)
    notes = db.Column(db.String(1000))
    
    user = db.relationship(User, backref='user_modules')
    module = db.relationship(Module, backref='user_modules')

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
        usermodule.last_viewed=datetime.utcnow()
        db.session.add(usermodule)
        db.session.commit()
        return usermodule

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    id_user_from = db.Column(db.Integer, db.ForeignKey(User.id))
    id_user_to = db.Column(db.Integer, db.ForeignKey(User.id))
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=True)
    sent_date = db.Column(db.DateTime)
    received_date = db.Column(db.DateTime)

    user_from = db.relationship(User, foreign_keys=[id_user_from], backref='sent_recommendations')
    user_to = db.relationship(User, foreign_keys=[id_user_to], backref='received_recommendations')
