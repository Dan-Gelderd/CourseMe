from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from courseme import app, db, lm, hash_string, lectures
import forms
from models import User, ROLE_USER, ROLE_ADMIN, Objective, Module, UserModule
from datetime import datetime
import json, operator
#import pdb; pdb.set_trace()        #DJG - remove

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = obj.isoformat()
        else:
            encoded_object =json.JSONEncoder.default(self, obj)
        return encoded_object


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
    catalogue = [row.as_dict() for row in Module.query.all()]                #DJG - confused over best way to do this http://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
    return render_template('index.html',
        title = title,
        catalogue = json.dumps(catalogue, cls=CustomEncoder, separators=(',',':')))


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
    #if request.method == 'POST':
    #    form.dynamic_list_select.choices = g.user.visible_objectives()     #DJG - this was part of an attempt to use a wtf selectmultiplefield to capture the prerequisite list in the hope this would be passed through the post request as an array of strings and so avoid using the comma delimited approach here. The coices need to be a list of tuples so this isn't in the right format.
    if form.validate():
        obj_id = form.edit_objective_id.data
        name = form.edit_objective_name.data
        #import pdb; pdb.set_trace()        #DJG - remove
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
                    is_are = 'is not already defined as an objective' if len(undefined_prerequisites) == 1 else 'are not already defined as objectives'
                    result['new_prerequisite'] = ["'" + "', '".join(undefined_prerequisites) + "' " + is_are]
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
                    is_are = 'is not already defined as an objective' if len(undefined_prerequisites) == 1 else 'are not already defined as objectives'
                    result['new_prerequisite'] = ["'" + "', '".join(undefined_prerequisites) + "' " + is_are]
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
@app.route('/editmodule/<int:id>', methods = ["GET", "POST"])
@login_required
def editmodule(id = 0):
    title = 'CourseMe - Edit Module'
    moduleform = forms.EditModule()         #DJG - need the arguement because using validate not validate_on_submit?
    #import pdb; pdb.set_trace()            #DJG - remove
    objectiveform = forms.EditObjective()
    module_objectives = []
    module = None
    form_header = "Create new module:"
    if id > 0:
        module = Module.query.get_or_404(id)
        if module:
            if module.author_id != g.user.id:
                flash('You are not authorised to edit this module')
                return redirect(url_for('module', id=id))
            elif request.method == 'GET':
                material_type = module.material_type
                form_header = "Edit " + material_type + ":"
                material_source = module.material_source
                material_path = module.material_path if material_source == 'youtube' else ''
                #flash(material_path)
                moduleform = forms.EditModule(
                    name = module.name,
                    description = module.description,
                    notes = module.notes,
                    material_type = module.material_type,
                    material_source = material_source,
                    material_path = material_path
                )
                module_objectives = module.objectives
        else:
            flash('There is no such module to edit')
            return redirect(url_for('index'))            

    if request.method == 'GET':       
        objectives = g.user.visible_objectives().all()
        objectives.sort(key=operator.methodcaller("score"))   #DJG - isn't there a way of doing this within the order_by of the query                 
        
        return render_template('editmodule.html',
                    title=title,
                    form_header = form_header,
                    edit_id=id,
                    objectives=objectives,
                    module = module,
                    module_objectives=module_objectives,
                    edit_module_form=moduleform,
                    objectiveform=objectiveform)
            
    if request.method == 'POST':
        
        #Both material upload types are required in the moduleform definition so need to remove the redundant field now to prevent validation errors

        #if material_source == 'upload':           #DJG - need a way to define the global list of sources so value means the same thing as database definitions 
        #    del moduleform.material_youtube
        #elif material_source == 'youtube':
        #    del moduleform.material_upload              
        #if moduleform.material_type.data == 'course':
        #    del moduleform.material_upload
        #    del moduleform.material_youtube

        if moduleform.validate():         
            objectives = []
            course_modules = []
            result = {}
            result['savedsuccess'] = False           
            proceed = False
            material_type = module.material_type if id > 0 else moduleform.material_type.data
            material_source = ""
            material_path = ""
            if material_type != "Course":
                #Reading off the list of objectives
                #DJG - try request.POST["objectives"] to see if data format is different
                unicode_list = request.form["objectives"]       #DJG - the data sent by the ajax request has the list converted into a unicode text string with commas
                python_list = filter(None, unicode_list.split(','))            #DJG - Dodgy string manipulation, means I can't have commas in objective names     
                if python_list: objectives = g.user.visible_objectives().filter(Objective.name.in_(python_list)).all()      #DJG - avoiding using the in_ operation when the list is empty as this is an inefficiency
                undefined_objectives = list(set(python_list) - set(obj.name for obj in objectives))     #DJG - Need to trap undefined objectives and return savedsucess as json if failed

                if undefined_objectives:       #DJG - code repeat of above, how to avoid this
                    is_are = 'is not already defined as an objetive' if len(undefined_objectives) == 1 else 'are not already defined as objetives'
                    result['objectives'] = ["'" + "', '".join(undefined_objectives) + "' " + is_are]
                    return json.dumps(result, separators=(',',':'))
              
                material_source = moduleform.material_source.data
                if module:
                    if module.material_source == material_source and material_source == "upload":    
                        material_path = module.material_path
                        
                if material_source == 'upload' and 'material' in request.files:             #DJG - Does flask-uploads automatically check against the allowed extention types and make the filename safe? Believe so.
                    material_path = lectures.save(request.files['material'])                 #This saves the file and returns its name (including the folder)            
                elif material_source == 'youtube' and moduleform.material_youtube.data:
                    material_path = moduleform.material_youtube.data
                    if not "?rel=0" in material_path: material_path=material_path+"?rel=0"      #DJG - Add this text string on to stop youtube videos showing followon videos directly in the iframe
                
                if material_path:
                    proceed = True
                    result['material'] = [material_path]
                else:
                    result['material'] = ["No content provided"]
                    
            else:
                unicode_list = request.form["course_modules"]       #DJG - the data sent by the ajax request has the list converted into a unicode text string with commas
                python_list = filter(None, unicode_list.split(','))  
                if python_list: course_modules = [Module.query.get(mod) for mod in python_list]     #DJG - need some validation here to make sure modules exist and are not themselves courses etc.
                proceed = True
                
            if proceed:
                if module:
                    module.name = moduleform.name.data
                    module.description = moduleform.description.data
                    module.notes = moduleform.notes.data
                    module.last_updated = datetime.utcnow()
                    module.material_source = material_source 
                    module.material_path = material_path
                    module.objectives = objectives
                    module.modules = []                 #DJG - need this to make the order of modules editable - or else need an association object in sqlalchamy to capture order as extra data of the many to many relationship
                    db.session.commit()
                    module.modules = course_modules

                else:
                    module = Module(name=moduleform.name.data,
                                    description = moduleform.description.data,
                                    notes = moduleform.notes.data,
                                    time_created=datetime.utcnow(),
                                    last_updated=datetime.utcnow(),
                                    author_id=g.user.id,
                                    material_type = material_type,
                                    material_source=material_source, 
                                    material_path=material_path,
                                    objectives=objectives,
                                    modules = course_modules)     
                    db.session.add(module)
                db.session.commit()
                result['savedsuccess'] = True
                result['module_id'] = module.id
                flash(material_type + " saved as " + module.name)
            
            return json.dumps(result, separators=(',',':'))
        
        else:
            moduleform.errors['savedsuccess'] = False
            return json.dumps(moduleform.errors, separators=(',',':'))


@app.route('/module/<int:id>')
@login_required
    #DJG - Login should not be required just temporary to stop user_module tracking breaking - need guest user
def module(id):
       
    module = Module.query.get(id)
    usermodule = UserModule.FindOrCreate(g.user.id, id) 
    templates = {"Lecture": "lecture.html", "Course": "course.html"}
    
    return render_template(templates[module.material_type],
                           module=module,
                           usermodule=usermodule)


@app.route('/star/<int:id>')
@login_required
def starclick(id):
    
    module = Module.query.get(id)
    user = g.user

    usermodule = UserModule.FindOrCreate(user.id, module.id)

    usermodule.starred = not usermodule.starred
    db.session.add(usermodule)
    db.session.commit()
    
    return usermodule.as_json()


@app.route('/vote/<int:id>')
@login_required
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


@app.route('/add-module-to-course/<int:module_id>/<int:course_id>')
@login_required
def add_module_to_course(module_id, course_id):
    result = {}
    result['savedsuccess'] = False
    course = Module.query.get(course_id)
    module = Module.query.get(module_id)
    #import pdb; pdb.set_trace()        #DJG - remove
    if module:
        if module.material_type == "Course":
            flash('You cannot embed a course within another course')
        else:
            if course:
                if course.author_id != g.user.id:
                    flash('You are not authorised to edit this course')
                elif course.material_type != "Course":
                    flask('You cannot add modules to a ' + course.material_type)
                else:
                    course_modules = course.modules.all()
                    course_modules.append(module)
                    course.modules = course_modules
                    course.last_updated=datetime.utcnow()
                    db.session.commit()
                    result['savedsuccess'] = True
            else:
                flash('No Course identified with id ' + course_id)
    else:
        flash('No Module identified with id ' + module_id)

    return json.dumps(result, separators=(',',':'))


@app.route('/test')
def test():
    return render_template('test.html')