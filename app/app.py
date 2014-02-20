#!/usr/bin/env python

from flask import Flask, render_template
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

@app.route('/testpage')
def test():
    return render_template('test.html')


@app.route('/modulestar/<name>')
def modulestarclick(name):
    
    module = datamodel.Module.find(name)
    user = datamodel.User.find("Student")
    try:
        usermodule = datamodel.UserModule.find(user, module)
    except KeyError:
        usermodule = datamodel.UserModule(user, module)

    usermodule.starred = not usermodule.starred
    usermodule.save()
    
    return json.dumps(usermodule.as_json(), sort_keys=True, default=str, separators=(',',':'))
    
def run_devserver():
    app.run(debug=True)

if __name__ == "__main__":
    run_devserver()