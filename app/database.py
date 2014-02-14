import datamodel

m = datamodel.Module("Test  Module")

m.author = datamodel.User("Test User")
m.save()


