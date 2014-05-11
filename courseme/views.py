from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from courseme import app, db, lm, hash_string, lectures
import forms
from models import User, ROLE_USER, ROLE_ADMIN, Objective, Module, UserModule
from datetime import datetime
import json, operator
#import pdb; pdb.set_trace()        #DJG - remove

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
                        name=form.username.data,
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
@login_required
def objectives():
    title = "CourseMe - Objectives"
    objectiveform = forms.EditObjective()
    objectives = g.user.visible_objectives().all()
    objectives.sort(key=operator.methodcaller("score"))   #DJG - isn't there a way of doing this within the order_by of the query
    return render_template('objectives.html',
                           title=title,
                           objectiveform=objectiveform,
                           objectives=objectives)

@app.route('/objective-add-update', methods = ['POST'])
def objective_add_update():
    form = forms.EditObjective()   
    #import pdb; pdb.set_trace()
    #form will be the fields of the html form with the csrf
    #request.form will be the data posted back through the ajax request
    #DJG - don't know why the request.form object seems to have a second empty edit_objective_id attribute
    if form.validate():
        obj_id = form.edit_objective_id.data
        name = form.edit_objective_name.data
        
        #Reading off the list of prerequisites
        unicode_list = request.form["prerequisites"]       #DJG - the data sent by the ajax request has the list converted into a unicode text string with commas
        python_list = filter(None, unicode_list.split(','))            #DJG - Dodgy string manipulation, means I can't have commas in objective names
        prerequisites = g.user.visible_objectives().filter(Objective.name.in_(python_list)).all()
        undefined_prerequisites = list(set(python_list) - set(obj.name for obj in prerequisites))
        result = {}
        result['savedsuccess'] = False
        if not obj_id:
            #The objective id is not found on the form so this is an add objective case
            check_obj = g.user.visible_objectives().filter_by(name = name).first()
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
                    #No need to check for cyclic prerequisites as the new objective cannot be a prerequisite to anything already
                    objective = Objective(name=name, prerequisites=prerequisites, created_by_id=g.user.id)
                    db.session.add(objective)
                    db.session.commit()
                    result['savedsuccess'] = True

        else:
            #The objective id is found on the form so this is an update objective case
            objective = Objective.query.get(obj_id)
            #DJG - should handle the case where no objective matches the id on the form request
            proceed = True
            #Check whether the user has the authority to edit it
            if g.user.role != ROLE_ADMIN and objective.created_by_id != g.user.id:
                result['edit_objective_name'] = ["You do not have authority to edit this objective"]
                proceed = False
            
            #Authorised to edit
            #Check whether the name has changed and if so check it is valid
            if proceed:
                if name != objective.name:
                    #Name has changed - need to check if new name already exists
                    check_obj = g.user.visible_objectives().filter_by(name = name).first()                  #DJG - code repeat of above, how to avoid this
                    if check_obj is not None:
                        #The new objective name is already taken
                        result['edit_objective_name'] = ["Objective '" + name + "' already exists"]
                        proceed = False
 
            #Name not changed or new name not taken
            if proceed:
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
    #DJG - need to check user has authority to delete objective
    objective = Objective.query.filter_by(id = request.args.get("objective_id")).first()        #DJG - could replace with get as we are looking up a primary key
    db.session.delete(objective)        #DJG - secondary table should be updated automatically because of relationship definintion
    db.session.commit()
    return ""

@app.route('/objective-get')
def objective_get():
    objective = Objective.query.filter_by(id = request.args.get("objective_id")).first()    #DJG - could replace with get as we are looking up a primary key
    return json.dumps(objective.as_dict(), sort_keys=True, separators=(',',':'))


#modules
@app.route('/editmodule', methods = ["GET", "POST"])
@login_required
def editmodule():
    title = 'CourseMe - Edit Module'
    moduleform = forms.EditModule()
    objectiveform = forms.EditObjective()
    #DJG - need to test for validate
    if moduleform.validate_on_submit() and 'material' in request.files:        #DJG - Does flask-uploads automatically check against the allowed extention types and make the filename safe? Believe so.
        name = lectures.save(request.files['material'])                 #This saves the file and returns its name (including the folder)

        #Reading off the list of objectives
        unicode_list = request.form["objectives"]       #DJG - the data sent by the ajax request has the list converted into a unicode text string with commas
        python_list = filter(None, unicode_list.split(','))            #DJG - Dodgy string manipulation, means I can't have commas in objective names
        objectives = g.user.visible_objectives().filter(Objective.name.in_(python_list)).all()
        undefined_objectives = list(set(python_list) - set(obj.name for obj in objectives))

        module = Module(name=moduleform.name.data,
                        time_created=datetime.utcnow(),
                        author_id=g.user.id,
                        material_path=name)     
        db.session.add(module)
        db.session.commit()
        #flash("Lecture saved as " + name)
        return redirect(url_for('module', id=module.id))

    objectives = g.user.visible_objectives().all()
    objectives.sort(key=operator.methodcaller("score"))   #DJG - isn't there a way of doing this within the order_by of the query    
    return render_template('editmodule.html',
                           title=title,
                           objectives=objectives,
                           edit_material_form=moduleform,
                           objectiveform=objectiveform)


@app.route('/module/<id>')
@login_required
    #DJG - Login should not be required just temporary
def module(id):
       
    module = Module.query.get(id)
    user = g.user

    usermodule = UserModule.FindOrCreate(user.id, id)
    
    #import pdb; pdb.set_trace()        #DJG - remove 
    
    return render_template('module.html',
                           module=module,
                           usermodule=usermodule)


@app.route('/star/<id>')
def starclick(id):
    
    module = Module.query.get(id)
    user = g.user

    usermodule = UserModule.FindOrCreate(user.id, module.id)

    usermodule.starred = not usermodule.starred
    db.session.add(usermodule)
    db.session.commit()
    
    return usermodule.as_json()


@app.route('/vote/<id>')
def voteclick(id):
    
    module = Module.query.get(id)
    user = g.user

    usermodule = UserModule.FindOrCreate(user.id, module.id)
    
    newVote = int(request.args.get("vote"))
    module.votes = module.votes - usermodule.vote + newVote       #DJG - Almost certainly a better way
    usermodule.vote = newVote
        
    db.session.add(usermodule)
    db.session.add(module)
    db.session.commit()
    
    return ""   #DJG - What is best return value when I don't care about the return result? Only thing I found that worked




#courses
@app.route('/editcourse/<int:id>', methods = ["GET", "POST"])
@login_required
def editcourse(id):
    title = 'CourseMe - Edit Course'
    form = forms.EditCourse()

    if form.validate_on_submit():
        result = {}
        result['savedsuccess'] = False
        if id > 0:
            course = Course.query.get(id)
            if course:
                course.name = form.name.data
                course.last_updated = datetime.utcnow()
            else:
                result['error'] = "This course could not be found and so has not been edited"
        else:
            course = Course(name=form.name.data,
                            time_created=datetime.utcnow(),
                            last_updated = datetime.utcnow(),
                            author_id=g.user.id)     
        db.session.add(course)
        db.session.commit()
        result['savedsuccess'] = True
        return redirect(url_for('course', id=course.id))

    return render_template('editcourse.html',
                           title=title,
                           edit_material_form=form)






@app.route('/test')
def test():
    objectiveform = forms.EditObjective()
    objectives = Objective.query.all()
    objectives.sort(key=operator.methodcaller("score"))
    return render_template('test.html',
                           objectives=objectives,
                           objectiveform=objectiveform)