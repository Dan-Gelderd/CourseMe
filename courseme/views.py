from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from courseme import app, db, lm, hash_string
import forms
from models import User, ROLE_USER, ROLE_ADMIN, Objective
from datetime import datetime
import json, operator
import datamodel
#import pdb; pdb.set_trace()

#admin
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user       #DJG - Could scrap this and just use current_user directly?
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/')
@app.route('/index')
#@login_required
def index():
    title = "CourseMe"
    user = g.user
    posts = [
        { 
            'author': { 'nickname': 'John' }, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': { 'nickname': 'Susan' }, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template('index.html',
        title = title,
        user = user,
        posts = posts)


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    title = 'CourseMe - Sign up'
    form = forms.SignupForm()
    if form.validate_on_submit():
        email_exist = User.query.filter_by(email=form.email.data).count()
        if email_exist:
            form.email.errors.append('This email address has already been registered')
            return render_template('signup.html', form = form, title = title)
        else:
            user = User(email=form.email.data,
                        password=hash_string(form.password.data),
                        username=form.username.data,
                        time_registered=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        role = ROLE_USER)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember = form.remember_me.data)
            flash("Successfully signed up.")
            return redirect(request.args.get("next") or url_for("index"))
    return render_template('signup.html', form=form, title=title)


@app.route("/login", methods=["GET", "POST"])
def login():
    title = 'CourseMe - Login'
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is None:
            form.email.errors.append('Email not registered')
            return render_template('login.html', form = form, title=title)
        if user.password != hash_string(form.password.data):
            form.password.errors.append('Incorrect password')
            return render_template('login.html', form = form, title=title)
        login_user(user, remember = form.remember_me.data)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("index"))       #DJG - next redirect doesn't seem to work eg. createmodule page
    return render_template('login.html', form=form, title=title)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#objectives
@app.route('/objectives')
#@login_required
def objectives():
    title = "CourseMe - Objectives"
    form = forms.AddUpdateObjective()
    objectives = Objective.query.all()
    objectives.sort(key=operator.methodcaller("score"))   #DJG - isn't there a way of doing this within the order_by of the query
    return render_template('objectives.html',
                           title=title,
                           form=form,
                           objectives=objectives)

@app.route('/objective-add-update', methods = ['POST'])
def objective_add_update():
    form = forms.AddUpdateObjective()   
    #import pdb; pdb.set_trace()
    #form will be the fields of the html form with the csrf
    #request.form will be the data posted back through the ajax request
    #DJG - don't know why the request.form object seems to have a second empty edit_objective_id attribute
    if form.validate():
        obj_id = form.edit_objective_id.data
        name = form.edit_objective_name.data
        prerequisites_unicode = request.form["prerequisites"]       #DJG - the data sent by the ajax request has the list of prerequisites converted into a unicode text string with commas
        prerequisites_list = filter(None, prerequisites_unicode.split(','))            #DJG - Dodgy string manipulation, measn I can't have commas in objective names
        prerequisites = Objective.query.filter(Objective.name.in_(prerequisites_list)).all()
        undefined_prerequisites = list(set(prerequisites_list) - set(obj.name for obj in prerequisites))
        result = {}
        result['savedsuccess'] = False
        #import pdb; pdb.set_trace()
        if not obj_id:
            #The objective id is not found on the form so this is an add objective case
            check_obj = Objective.query.filter_by(name = name).first()
            if check_obj is not None:
                #The new objective name is already taken
                result['edit_objective_name'] = ["Objective '" + name + "' already exists"]     #Need to make the new result attributes the same as the form.errors attributes which will be the form input field ids
            else:
                #A new objective can be created with the new name
                #Need to check all the prerequisites exist already
                if undefined_prerequisites:
                    is_are = 'is' if len(undefined_prerequisites) == 1 else 'are'
                    result['new_prerequisite'] = ["'" + "', '".join(undefined_prerequisites) + "' " + is_are + " not already defined"]
                else:
                    objective = Objective(name=name, prerequisites=prerequisites)
                    db.session.add(objective)
                    db.session.commit()
                    result['savedsuccess'] = True

        else:
            #The objective id is found on the form so this is an update objective case
            objective = Objective.query.get(obj_id)
            new_name_valid = True
            #Check whether the name has changed
            if name != objective.name:
                #Name has changed - need to check if new name already exists
                check_obj = Objective.query.filter_by(name = name).first()                  #DJG - code repeat of above, how to avoid this
                if check_obj is not None:
                    #The new objective name is already taken
                    result['edit_objective_name'] = ["Objective '" + name + "' already exists"]
                    new_name_valid = False
            if new_name_valid:
                #Name not changed or new name not taken
                #Need to check all the prerequisites exist already
                if undefined_prerequisites:       #DJG - code repeat of above, how to avoid this
                    is_are = 'is' if len(undefined_prerequisites) == 1 else 'are'
                    result['new_prerequisite'] = ["'" + "', '".join(undefined_prerequisites) + "' " + is_are  + " not already defined"]
                else:
                    #Need to check for cyclic prerequisites
                    cyclic_prerequisites = [p.name for p in prerequisites if p.is_required_indirect(objective)]
                    if cyclic_prerequisites:       
                        is_are = 'is' if len(cyclic_prerequisites) == 1 else 'are'
                        result['new_prerequisite'] = ["'" + "', '".join(cyclic_prerequisites) + "' " + is_are + " dependent on the current objective"]
                    else:
                        objective.name = name
                        objective.prerequisites = prerequisites
                        db.session.add(objective)
                        db.session.commit()                    
                        result['savedsuccess'] = True
            
        return json.dumps(result, separators=(',',':'))
 
    form.errors['savedsuccess'] = False
    return json.dumps(form.errors, separators=(',',':'))


@app.route('/objective-delete')
def objective_delete():
    objective = Objective.query.filter_by(id = request.args.get("objective_id")).first()
    db.session.delete(objective)        #DJG - secondary table should be updated automatically because of relationship definintion
    db.session.commit()
    return ""

@app.route('/objective-get')
def objective_get():
    objective = Objective.query.filter_by(id = request.args.get("objective_id")).first()
    return json.dumps(objective.as_dict(), sort_keys=True, separators=(',',':'))


#modules
@app.route('/createmodule')
@login_required
def createmodule():
    title = 'CourseMe - Create Module'
    form = forms.CreateModule()

    return render_template('createmodule.html',
                           title=title,
                           form=form)


@app.route('/module/<name>')
def module(name):
    
    module = datamodel.Module.find(name)
    user = datamodel.User.find("Student")
    try:
        usermodule = datamodel.UserModule.find(user, module)
    except KeyError:
        usermodule = datamodel.UserModule(user, module)

    authormodule = datamodel.UserModule.find(module.author, module)

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
    
    newVote = int(flask.request.args.get("vote"))
    module.votes = module.votes - usermodule.vote + newVote       #DJG - Almost certainly a better way
    usermodule.vote = newVote
        
    usermodule.save()
    module.save
    
    return ""   #DJG - What is best return value when I don't care about the return result? Only thing I found that worked



@app.route('/autocomplete')
def autocomplete():
    return render_template('Test/autocomplete.html')