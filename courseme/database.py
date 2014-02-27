import datamodel


#Create objectives 1 to 10 where 1 is prerequisite of 2, 3 of 4 etc and 2 is also of 4
for x in range(1,9,1):
    o = datamodel.Objective("Objective " + str(x))
    o.save()

for x in range(2,9,2):
    o = datamodel.Objective.find("Objective " + str(x))
    o.prerequisites = set([datamodel.Objective.find("Objective " + str(x-1))])
    o.save()
    
for x in range(4,9,4):
    o = datamodel.Objective.find("Objective " + str(x))
    o.prerequisites = set([datamodel.Objective.find("Objective " + str(x-1)), datamodel.Objective.find("Objective " + str(x-2))])
    o.save()


u = datamodel.User("Author")
u.save()

u = datamodel.User("Tutor")
u.save()

u = datamodel.User("Student")
u.save()

#Create modules with objectives
for x in range(1,5,1):
    m = datamodel.Module("Module" + str(x))
    m.author = datamodel.User.find("Author")
    m.objectives = set([datamodel.Objective.find("Objective " + str(x)), datamodel.Objective.find("Objective " + str(x + 4))])
    m.votes = x*10
    m.save()

um = datamodel.UserModule(datamodel.User.find("Student"), datamodel.Module.find("Module1"))
um.starred=True
um.vote=1
um.notes = "I am doing this module and it is great"
um.save()

for x in range(1, 5, 1):
    um = datamodel.UserModule(datamodel.User.find("Author"), datamodel.Module.find("Module" + str(x)))
    um.starred=False
    um.vote=0
    um.notes = "I wrote this module and it is great"
    um.save()



