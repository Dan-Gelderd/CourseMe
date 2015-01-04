#!flask/bin/python
from courseme import app, db, models
from flask.ext.script import Manager, Shell

manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, User=models.User, Module=models.Module, Objective=models.Objective)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
