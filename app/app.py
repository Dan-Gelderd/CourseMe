#!/usr/bin/env python

from flask import Flask, render_template, request
import datamodel
import database
import json

app = Flask(__name__, static_folder="../static", static_url_path="/static")


def search_objective(objective):
    return {'lectures':[2, 3, 4], 'exercises':[2, 3, 4], 'tools':[2, 3, 4]}

def alternative_modules(module, user):
    alternative_modules={}
    for objective in module.objectives:
        alternative_modules[objective]=search_objectives(objective)
    return alternative_modules

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/module/<name>')
def module(name):
    
    module = datamodel.Module.find(name)
    user = datamodel.User.find("Student")
    try:
        usermodule = datamodel.UserModule.find(user, module)
    except KeyError:
        usermodule = datamodel.UserModule(user, module)

    authormodule = datamodel.UserModule.find(module.author, module)
    #tutormodule = datamodel.UserModule.find(module.author, module)    

    return render_template('module.html',
                           module=module,
                           usermodule=usermodule,
                           authormodule=authormodule,
    )


@app.route('/star/<name>')
def starclick(name):
    
    module = datamodel.Module.find(name)
    user = datamodel.User.find("Student")
    try:
        usermodule = datamodel.UserModule.find(user, module)
    except KeyError:
        usermodule = datamodel.UserModule(user, module)

    usermodule.starred = not usermodule.starred
    usermodule.save()
    
    return usermodule.as_json()

@app.route('/vote/<name>')
def voteclick(name):
    
    module = datamodel.Module.find(name)
    user = datamodel.User.find("Student")
    try:
        usermodule = datamodel.UserModule.find(user, module)
    except KeyError:
        usermodule = datamodel.UserModule(user, module)
    
    newVote = int(request.args.get("vote"))
    module.votes = module.votes - usermodule.vote + newVote       #DJG - Almost certainly a better way
    usermodule.vote = newVote
        
    usermodule.save()
    module.save
    
    return ""   #DJG - What is best return value when I don't care about the return result? Only thing I found that worked
    
def run_devserver():
    app.run(debug=True)

if __name__ == "__main__":
    run_devserver()