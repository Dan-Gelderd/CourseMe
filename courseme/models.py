from courseme import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    last_seen =  db.Column(db.DateTime)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def __repr__(self):
        return '<User %r>' % (self.nickname)
    
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

objective_heirarchy = db.Table("objective_heirarchy",
    db.Column("prerequisite_id", db.Integer, db.ForeignKey("objective.id")),
    db.Column("followon_id", db.Integer, db.ForeignKey("objective.id"))
)

class Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique = True)
    prerequisites = db.relationship("Objective",
                        secondary=objective_heirarchy,
                        primaryjoin=(objective_heirarchy.c.followon_id==id),
                        secondaryjoin=(objective_heirarchy.c.prerequisite_id==id),
                        #backref = db.backref('followons', lazy = 'dynamic'), 
                        lazy = 'dynamic')
    

    def require(self, objective):
        if not self.is_required(objective):
            self.prerequisites.append(objective)
            return self

    def unrequire(self, objective):
        if self.is_required(objective):
            self.prerequisites.remove(objective)
            return self

    def is_required(self, objective):
        return self.prerequisites.filter(objective_heirarchy.c.prerequisite_id == objective.id).count() > 0

