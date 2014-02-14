#!/usr/bin/env python

from flask import Flask, render_template
import datamodel
#from courseme import 

app = Flask(__name__, static_folder="../static", static_url_path="/static")

global_objectives = {
    0: "Evaluate a function for a given value of the input variable - app",
    1: "Use function notation to denote the output of a function - app",
    2: "Some objective",
    3: "Some other objective",
    4: "Some earlier objective",
}

modules={
    0: {'name': "Next module - app",},
    1: {'name': "Previous module with an inconveniently long name - app",},
    2: {'name': "Alt - app",},
    3: {'name': "Alt 2 - app",},
    4: {'name': "Alt 3 - app",},
    5: {'name': "This module - app",},
}

users={
    0: {'name': "Zippy - app", 'institution': "Rainbow High School", 'blurb': "I'm a private tutor working in South London"},
    1: {'name': "Lizzy", 'institution': "Cool School"},
}

def search_objective(objective):
    return {'lectures':[2, 3, 4], 'exercises':[2, 3, 4], 'tools':[2, 3, 4]}

def alternative_modules(module, user):
    alternative_modules={}
    for objective in module.objectives:
        alternative_modules[objective]=search_objectives(objective)
    return alternative_modules

module = {
        'index': 5,        
        'name': 'Module name from app',
        'votes':333,
        'objectives': [0, 1],
        'prerequisites': [2, 3, 4],        
        'next_module': 0,
        'previous_module': 1,
        'author': 0,
    }

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/module/<name>')
def module(name):
    
    module = datamodel.Module.find(name)
    
    module['alternatives'] = alternative_modules(module, 0)      #DJG - Hard coded
    
    module_user = {
        'starred': True,
        'last_used': 01/01/2014,
        'recommended_by': 1,
    }

    return render_template('module.html',
                           module=module,
                           module_user=module_user,
                           modules=modules,
                           global_objectives=global_objectives,
                           users=users
    )


def run_devserver():
    app.run(debug=True)

if __name__ == "__main__":
    run_devserver()