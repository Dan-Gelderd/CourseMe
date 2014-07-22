#!flask/bin/python
from courseme import db, hash_string
from courseme.models import Module, User, ROLE_USER, ROLE_ADMIN, Objective, Institution
from datetime import datetime

user = User(email="support@courseme.com",
            password=hash_string("111111"),
            name="CourseMe",
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_ADMIN)
db.session.add(user)

me = User(email="dan.gelderd@courseme.com",
            password=hash_string("111111"),
            name="Dan Gelderd",
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_ADMIN)
db.session.add(me)

user = User(email="dan@server.fake",
            password=hash_string("111111"),
            name="Dan",
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_USER)
db.session.add(user)

user = User(email="liz@server.fake",
            password=hash_string("111111"),
            name="Liz",
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_USER)
db.session.add(user)

student = User(email="student@server.fake",
            password=hash_string("111111"),
            name="Student",
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_USER)
db.session.add(student)

db.session.commit()

institution = Institution.create(
    name = "CourseMe",
    creator = User.main_admin_user(),
    blurb = "This is the main CourseMe institution"
    )

objective = Objective(name="System Objective 1",
                      created_by_id=User.main_admin_user().id)
db.session.add(objective)
db.session.commit()

objective = Objective(name="System Objective 2",
                      created_by_id=User.main_admin_user().id,
                      prerequisites=[Objective.query.get(1)]
                      )
db.session.add(objective)

objective = Objective(name="System Objective 3",
                      created_by_id=User.main_admin_user().id,
                      prerequisites=[Objective.query.get(1)]
                      )
db.session.add(objective)

db.session.commit()

module = Module(
    name="Different sized infinities",
    description = "Vi Hart Lecture from youtube",
    notes = "This is just a placeholder",
    time_created=datetime.utcnow(),
    last_updated=datetime.utcnow(),
    author_id=me.id,
    material_type = "Lecture",
    material_source="youtube", 
    material_path="//www.youtube.com/embed/lA6hE7NFIK0?list=UUOGeU-1Fig3rrDjhm9Zs_wg",
    objectives=[Objective.query.get(1)]
    )
db.session.add(module)

module = Module(
    name="Hexaflexagons",
    description = "Vi Hart Lecture from youtube",
    notes = "This is just a placeholder",
    time_created=datetime.utcnow(),
    last_updated=datetime.utcnow(),
    author_id=me.id,
    material_type = "Lecture",
    material_source="youtube", 
    material_path="//www.youtube.com/embed/VIVIegSt81k?rel=0",
    objectives=[Objective.query.get(2)]
    )
db.session.add(module)

module = Module(
    name="Binary Trees",
    description = "Vi Hart Lecture from youtube",
    notes = "This is just a placeholder",
    time_created=datetime.utcnow(),
    last_updated=datetime.utcnow(),
    author_id=me.id,
    material_type = "Lecture",
    material_source="youtube", 
    material_path="//www.youtube.com/embed/e4MSN6IImpI?list=PLF7CBA45AEBAD18B8",
    objectives=[Objective.query.get(3)]
    )
db.session.add(module)

db.session.commit()

institution.add_member(me)

institution.add_student(student)

print me.live_modules_authored().all()

print me.live_modules_viewed().all()

print me.visible_modules().all()
