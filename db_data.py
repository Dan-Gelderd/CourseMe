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
            blurb="I built the CourseMe website and now am fabulously rich.",
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

head = User(email="head@server.fake",
            password=hash_string("111111"),
            name="Head of School",
            blurb="I have been Headmaster at High School for five years. I'm great.",
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_USER)
db.session.add(head)
db.session.commit()

courseMe = Institution.create(
    name = "CourseMe",
    creator = User.main_admin_user(),
    blurb = "This is the main CourseMe institution"
    )

school = Institution.create(
    name = "High School",
    creator = head,
    blurb = "This is a great High School. We use CourseMe for everything. We have 100 pupils and they're all doing great."
    )

for i in range(1, 3):
    teacher = User(email="teacher" + str(i) + "@server.fake",
            password=hash_string("111111"),
            name="Mrs. Blogs " + str(i),
            blurb="I have been a teacher at High School for five years. I'm great.",
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_USER)
    db.session.add(teacher)
    
    school.add_member(teacher)


for i in range(1, 100):
    student = User(email="student" + str(i) + "@server.fake",
            password=hash_string("111111"),
            name="Student"+str(i),
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_USER)
    db.session.add(student)

    school.add_student(student,True)

db.session.add(school)
db.session.commit() 

parent = User(email="parent@server.fake",
            password=hash_string("111111"),
            name="Parent",
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_USER)
parent.students.append(student)

db.session.add(parent)

db.session.commit()





objective = Objective(name="Rationalise the denominator of fractions with surds",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id
                      #prerequisites=[Objective.query.get(2)]
                      )
db.session.add(objective)
db.session.commit()

objective = Objective(name="Estimate powers and roots of any given positive",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id
                      #prerequisites=[Objective.query.get(2)]
                      )
db.session.add(objective)
db.session.commit()

objective = Objective(name="Convert terminating decimals to their corresponding fractions",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id
                      #prerequisites=[Objective.query.get(2)]
                      )
db.session.add(objective)
db.session.commit()

objective = Objective(name="Identify and work with fractions in ratio problems",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id
                      #prerequisites=[Objective.query.get(2)]
                      )
db.session.add(objective)
db.session.commit()

objective = Objective(name="Use and interpret algebraic notation",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id
                      #prerequisites=[Objective.query.get(2)]
                      )
db.session.add(objective)
db.session.commit()

objective = Objective(name="Substitute numerical values into formulae and expressions, including scientific formulae",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id
                      #prerequisites=[Objective.query.get(2)]
                      )
db.session.add(objective)
db.session.commit()

objective2 = Objective(name="Substitute algebraic expressions into formulae and expressions, including scientific formulae",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id,
                      prerequisites=[objective]
                      )
db.session.add(objective2)
db.session.commit()

objective = Objective(name="Round numbers and measures to an appropriate degree of accuracy",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id
                      #prerequisites=[Objective.query.get(2)]
                      )
db.session.add(objective)
db.session.commit()

objective2 = Objective(name="Use inequality notation to specify simple error intervals due to truncation or rounding",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id,
                      prerequisites=[objective]
                      )
db.session.add(objective2)
db.session.commit()

objective = Objective(name="Apply and interpret limits of accuracy",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id
                      #prerequisites=[Objective.query.get(2)]
                      )
db.session.add(objective)
db.session.commit()

objective = Objective(name="Rearrange formulae to change the subject",
                      subject="Mathematics",
                      created_by_id=User.main_admin_user().id
                      #prerequisites=[Objective.query.get(2)]
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
    objectives=[Objective.query.get(1)],
    extension = True
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
    objectives=[Objective.query.get(2)],
    extension = True
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
    objectives=[Objective.query.get(3)],
    extension = True
    )
db.session.add(module)

module = Module(
    name="How I feel about Logarithms",
    description = "Vi Hart Lecture from youtube",
    notes = "This is just a placeholder",
    time_created=datetime.utcnow(),
    last_updated=datetime.utcnow(),
    author_id=me.id,
    material_type = "Lecture",
    material_source="youtube", 
    material_path="//www.youtube-nocookie.com/embed/N-7tcTIrers?rel=0",
    objectives=[Objective.query.get(3)],
    extension = True
    )
db.session.add(module)


module = Module(
    name="Solving Linear Equations",
    description = "An easy introduction to solving simple equations with one unknown",
    notes = "Here are some notes about this lecture",
    time_created=datetime.utcnow(),
    last_updated=datetime.utcnow(),
    author_id=teacher.id,
    material_type = "Lecture",
    material_source="youtube", 
    material_path="//www.youtube-nocookie.com/embed/0BsoWvWXOMM?rel=0",
    objectives=[Objective.query.get(3)]
    )
db.session.add(module)  

module = Module(
    name="Solving Linear Equations",
    description = "An easy introduction to solving simple equations with one unknown",
    notes = "Here are some notes about this lecture",
    time_created=datetime.utcnow(),
    last_updated=datetime.utcnow(),
    author_id=head.id,
    material_type = "Lecture",
    material_source="youtube", 
    material_path="//www.youtube-nocookie.com/embed/GmMX3-nTWbE?rel=0",
    objectives=[Objective.query.get(3)]
    )
db.session.add(module)  

module = Module(
    name="Adding Fractions",
    description = "A foolproof way to add and subtract numerical fractions",
    notes = "Here are some notes about this lecture",
    time_created=datetime.utcnow(),
    last_updated=datetime.utcnow(),
    author_id=teacher.id,
    material_type = "Lecture",
    material_source="youtube", 
    material_path="//www.youtube-nocookie.com/embed/52ZlXsFJULI?rel=0",
    objectives=[Objective.query.get(3)]
    )
db.session.add(module)  

module = Module(
    name="Simple Trigonometry",
    description = "An introduction to trigonometry functions for a right angled triangle",
    notes = "Here are some notes about this lecture",
    time_created=datetime.utcnow(),
    last_updated=datetime.utcnow(),
    author_id=teacher.id,
    material_type = "Lecture",
    material_source="youtube", 
    material_path="//www.youtube-nocookie.com/embed/F21S9Wpi0y8?rel=0",
    objectives=[Objective.query.get(3)]
    )
db.session.add(module)


db.session.commit()

courseMe.add_member(me)

school.add_member(teacher)

