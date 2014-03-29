#!flask/bin/python
from courseme import db, hash_string
from courseme.models import User, ROLE_USER, ROLE_ADMIN, Objective
from datetime import datetime

user = User(email="admin@courseme.com",
            password=hash_string("111111"),
            name="admin",
            time_registered=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            role = ROLE_ADMIN)
db.session.add(user)

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

db.session.commit()

objective = Objective(name="System Objective 1",
                      created_by_id=User.query.filter_by(name="admin").first().id)
db.session.add(objective)

objective = Objective(name="System Objective 2",
                      created_by_id=User.query.filter_by(name="admin").first().id)
db.session.add(objective)

objective = Objective(name="System Objective 3",
                      created_by_id=User.query.filter_by(name="admin").first().id)
db.session.add(objective)

db.session.commit()

