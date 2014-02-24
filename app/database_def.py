from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Table, Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///courseme.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

objective_heirarchy = Table("objective_heirarchy", Base.metadata,
    Column("prerequisite_id", Integer, ForeignKey("objectives.id"), primary_key=True),
    Column("followon_id", Integer, ForeignKey("objectives.id"), primary_key=True)
)

class Objective(Base):
    __tablename__ = 'objectives'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    prerequisites = relationship("Objective",
                        secondary=objective_heirarchy,
                        primaryjoin=id==objective_heirarchy.c.followon_id,
                        secondaryjoin=id==objective_heirarchy.c.prerequisite_id
    )


class Institution(Base):
    __tablename__ = "institutions"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    blurb = Column(String)

Base.metadata.create_all(engine)

institution = Institution(name="Test Institution", blurb="...")
session.add(institution)
session.commit()

#session.query(Objective).all().delete()
#session.commit()

o1 = Objective(name="obj1", prerequisites=[])
o2 = Objective(name="obj2", prerequisites=[])
o3 = Objective(name="obj3", prerequisites=[])
o4 = Objective(name="obj4", prerequisites=[])

session.add(o1)
session.add(o2)
session.add(o3)
session.add(o4)
session.commit()

o2.prerequisites.append(o1)
o3.prerequisites.append(o1)
o4.prerequisites.append(o1)
o4.prerequisites.append(o2)
o4.prerequisites.append(o3)

session.commit()

session.close()