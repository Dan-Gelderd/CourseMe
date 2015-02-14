from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from . import main
from .. import db, lectures
import forms
from .. models import User, ROLE_USER, ROLE_ADMIN, Objective, SchemeOfWork, UserObjective, Module, UserModule, Institution, \
    Group, Message, Question, Subject, Topic
from datetime import datetime
import operator
from ..email import send_email

import courseme.util.json as json

# import pdb; pdb.set_trace()        #DJG - remove

@main.route('/layout')
def layout():
    title = "CourseMe"
    return render_template('layout.html',
                           title=title)

@main.route('/')
@main.route('/index')
def index():
    title = "CourseMe"
    if g.user.is_authenticated():
        modules = g.user.visible_modules().all()
    else:
        modules = Module.LiveModules().all()

    catalogue = [mod.as_dict() for mod in modules]
    # DJG - confused over best way to do this http://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
    return render_template('index.html',
                           title=title,
                           modules=modules,
                           # DJG - temporary; unless there is a way to pass datatables a list of objects
                           catalogue=json.dumps(catalogue))


@main.route('/select-subject/<int:id>', methods=["POST"])
@login_required
def select_subject(id):
    if id > 0: subject = Subject.query.get(id)
    if subject:
        g.user.subject_id = subject.id
        db.session.add(g.user)
        db.session.commit()
        print subject.id, subject.name, g.user.name
    return ""


# objectives
@main.route('/objectives-admin')
@login_required
def objectives_admin():
    title = "CourseMe - Objectives"
    objectiveform = forms.EditObjective()
    objectiveform.edit_objective_topic.choices = Topic.TopicChoices(
        g.user)  # DJG - need to include this extra line everywhere to populate the objective topic choices. Can't do this in forms or models directy as no knowledge of tyhe session variable and so user in those places?
    objectives = g.user.visible_objectives().all()
    objectives.sort(
        key=operator.methodcaller("score"))  # DJG - isn't there a way of doing this within the order_by of the query
    return render_template('objectivesadmin.html',
                           title=title,
                           objectiveform=objectiveform,
                           objectives=objectives)


@main.route('/objectives/<int:profile_id>')
@main.route('/objectives/<int:profile_id>/<int:scheme_id>')
@login_required
def objectives(profile_id, scheme_id=0):
    profile = User.query.get(profile_id)
    if not profile:
        flash("This user does not exist")
        return redirect(url_for('.objectives', profile_id=g.user.id))
    elif not profile.permission(g.user):
        flash("You do not have permission to view this user's learning objectives")
        return redirect(url_for('.objectives', profile_id=g.user.id))
    else:
        title = "CourseMe - Objectives"
        objectiveform = forms.EditObjective()
        objectiveform.edit_objective_topic.choices = Topic.TopicChoices(
            g.user)  # DJG - need to include this extra line everywhere to populate the objective topic choices. Can't do this in forms or models directy as no knowledge of tyhe session variable and so user in those places?
        objectives = []
        if scheme_id == 0:
            objectives = g.user.visible_objectives().all()
        else:
            scheme = SchemeOfWork.query.get(scheme_id)
            if scheme:
                objectives = scheme.objectives.all()
            else:
                flash("Scheme of work not found")
                return redirect(url_for('.schemes'))
        objectives.sort(
            key=operator.methodcaller(
                "score"))  # DJG - isn't there a way of doing this within the order_by of the query
        return render_template(
            'objectives.html',
            title=title,
            objectiveform=objectiveform,
            objectives=objectives,
            profile=profile,
            scheme_id=scheme_id)


@main.route('/objectives-group/<int:group_id>')
@main.route('/objectives-group/<int:group_id>/<int:scheme_id>')
@main.route('/objectives-group/<int:group_id>/<int:scheme_id>/<int:name_display>')
@login_required
def objectives_group(group_id, scheme_id=0, name_display=1):
    if group_id == 0:
        group = {"id": 0, "name": "All Students"}
        profiles = g.user.all_students()
    else:
        group = Group.query.get(group_id)
        if not group:
            flash("This group does not exist")
            return redirect(url_for('.groups'))
        else:
            profiles = group.viewable_members()
        if len(profiles) == 0:
            flash("You do not have permission to view any of these users' learning objectives")
            return redirect(url_for('.groups'))

    title = "CourseMe - Objectives"
    objectives = []
    if scheme_id == 0:
        objectives = g.user.visible_objectives().all()
    else:
        scheme = SchemeOfWork.query.get(scheme_id)
        if scheme:
            objectives = scheme.objectives.all()
        else:
            flash("Scheme of work not found")
            return redirect(url_for('.schemes'))
    objectives.sort(
        key=operator.methodcaller("score"))  # DJG - isn't there a way of doing this within the order_by of the query
    return render_template(
        'objectives_group.html',
        title=title,
        objectives=objectives,
        profiles=profiles,
        scheme_id=scheme_id,
        name_display=name_display,
        group=group)


@main.route('/objective-add-update', methods=['POST'])
def objective_add_update():
    form = forms.EditObjective()
    form.edit_objective_topic.choices = Topic.TopicChoices(
        g.user)  # DJG - need to include this extra line everywhere to populate the objective topic choices. Can't do this in forms or models directy as no knowledge of tyhe session variable and so user in those places?
    form.edit_objective_prerequisites.choices = [(i, i) for i in form.edit_objective_prerequisites.data]
    # import pdb; pdb.set_trace()
    #form will be the fields of the html form with the csrf
    #request.form will be the data posted back through the ajax request
    #DJG - don't know why the request.form object seems to have a second empty edit_objective_id attribute
    #if request.method == 'POST':
    #    form.dynamic_list_select.choices = g.user.visible_objectives()     #DJG - this was part of an attempt to use a wtf selectmultiplefield to capture the prerequisite list in the hope this would be passed through the post request as an array of strings and so avoid using the comma delimited approach here. The coices need to be a list of tuples so this isn't in the right format.
    if form.validate():
        obj_id = form.edit_objective_id.data
        name = form.edit_objective_name.data
        topic = Topic.query.get(form.edit_objective_topic.data)
        topic_id = topic.id if topic else None
        prerequisites = []
        select_list = form.edit_objective_prerequisites.data
        if select_list: prerequisites = g.user.visible_objectives().filter(Objective.name.in_(select_list)).all()
        undefined_prerequisites = list(set(select_list) - set(obj.name for obj in prerequisites))
        result = {'savedsuccess': False}
        if not obj_id:
            #The objective id is not found on the form so this is an add objective case
            check_obj = g.user.visible_objectives().filter_by(name=name).first()
            if check_obj is not None:
                #The new objective name is already taken
                result['edit_objective_name'] = [
                    "Objective '" + name + "' already exists"]  #Need to make the new result attributes the same as the form.errors attributes which will be the form input field ids
            elif undefined_prerequisites:
                #A new objective can be created with the new name
                #Need to check all the prerequisites exist already                
                is_are = 'is not already defined as an objective' if len(
                    undefined_prerequisites) == 1 else 'are not already defined as objectives'
                result['new_prerequisite'] = ["'" + "', '".join(undefined_prerequisites) + "' " + is_are]
                #No need to check for cyclic prerequisites as the new objective cannot be a prerequisite to anything already
            elif topic and topic.subject_id != g.user.subject_id:
                result['edit_objective_subject'] = [g.user.subject_id]
            else:
                objective = Objective(name=name,
                                      subject_id=g.user.subject_id,
                                      topic_id=topic_id,
                                      prerequisites=prerequisites,
                                      created_by_id=g.user.id
                )
                db.session.add(objective)
                db.session.commit()
                result['savedsuccess'] = True

        else:
            #The objective id is found on the form so this is an update objective case
            #No need for any checks around the subject because this cannot be edited for an existing objective
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
                    check_obj = g.user.visible_objectives().filter_by(
                        name=name).first()  #DJG - code repeat of above, how to avoid this
                    if check_obj is not None:
                        #The new objective name is already taken
                        result['edit_objective_name'] = ["Objective '" + name + "' already exists"]
                        proceed = False

            #Name not changed or new name not taken            
            if proceed:
                #Need to check user.subject is the same as the existing objective subject
                if g.user.subject_id != objective.subject_id or (topic and topic.subject_id != objective.subject_id):
                    result['edit_objective_subject'] = [objective.subject_id]
                    proceed = False

            #User subject same as exsting objective subject
            if proceed:
                #Need to check all the prerequisites exist already            
                if undefined_prerequisites:  #DJG - code repeat of above, how to avoid this
                    is_are = 'is not already defined as an objective' if len(
                        undefined_prerequisites) == 1 else 'are not already defined as objectives'
                    result['new_prerequisite'] = ["'" + "', '".join(undefined_prerequisites) + "' " + is_are]
                else:
                    #Need to check for cyclic prerequisites
                    cyclic_prerequisites = [p.name for p in prerequisites if p.is_required_indirect(objective)]
                    if cyclic_prerequisites:
                        is_are = 'is' if len(cyclic_prerequisites) == 1 else 'are'
                        result['new_prerequisite'] = ["'" + "', '".join(
                            cyclic_prerequisites) + "' " + is_are + " dependent on the current objective"]
                    else:
                        objective.name = name
                        objective.prerequisites = prerequisites
                        objective.topic_id = topic_id
                        db.session.add(objective)
                        db.session.commit()
                        result['savedsuccess'] = True

        return json.dumps(result)

    form.errors['savedsuccess'] = False
    return json.dumps(form.errors)

                # form_header = "Edit " + material_type + ":"
                # material_source = module.material_source
                # material_path = module.material_path if material_source == 'youtube' else ''
                # #flash(material_path)
                # moduleform = forms.EditModule(
                #     name=module.name,
                #     description=module.description,
                #     notes=module.notes,
                #     material_type=module.material_type,
                #     material_source=material_source,
                #     material_path=material_path,
                #     subtitles=module.subtitles,
                #     easy_language=module.easy_language,
                #     extension=module.extension,
                #     for_teachers=module.for_teachers
                # )
                # module_objectives = module.objectives

@main.route('/objective-delete')
def objective_delete():
    # DJG - need to check user has authority to delete objective
    objective = Objective.query.get(request.args.get("objective_id"))
    db.session.delete(
        objective)  #DJG - secondary table should be updated automatically because of relationship definintion
    db.session.commit()
    return ""


@main.route('/objective-get')
def objective_get():
    objective = Objective.query.get(request.args.get("objective_id"))
    return json.dumps(objective.as_dict(), sort_keys=True)


@main.route('/objective-assess/<int:profile_id>/<int:objective_id>')
@login_required
def objective_assess(profile_id, objective_id):
    objective = Objective.query.get(objective_id)  # DJG - may restrict search to just some set of visisble objectives
    if not objective:
        flash("This objective does not exist")
        return redirect(url_for('.objectives', id=g.user.id))
    profile = User.query.get(profile_id)
    if not profile:
        flash("This user does not exist")
        return redirect(url_for('.objectives', id=g.user.id))
    elif not profile.permission(g.user):
        flash("You do not have permission to view this user's learning objectives")
        return redirect(url_for('.objectives', id=g.user.id))
    else:
        userobjective = UserObjective.FindOrCreate(profile_id, g.user.id, objective_id)
        userobjective.assess()
        # import pdb; pdb.set_trace()
        return json.dumps({
            'assessed_display_class': userobjective.assessed_display_class(),
            'assessed': userobjective.completed
        })


# modules
@main.route('/editmodule/<int:id>', methods=["GET", "POST"])
@login_required
def editmodule(id=0):
    title = 'CourseMe - Edit Module'
    moduleform = forms.EditModule()  #DJG - need the arguement because using validate not validate_on_submit?
    #import pdb; pdb.set_trace()            #DJG - remove
    objectiveform = forms.EditObjective()
    objectiveform.edit_objective_topic.choices = Topic.TopicChoices(
        g.user)  #DJG - need to include this extra line everywhere to populate the objective topic choices. Can't do this in forms or models directy as no knowledge of tyhe session variable and so user in those places?
    module_objectives = []
    module = None
    if not g.user.subject:
        flash("You need to select what subject you are interested in")
        return redirect(url_for('.index'))

    form_header = "Create new " + g.user.subject.name + " module:"
    if id > 0:
        module = Module.query.get(id)
        if module:
            if module.author_id != g.user.id:
                flash('You are not authorised to edit this module')
                return redirect(url_for('.module', id=id))
            elif request.method == 'GET':
                g.user.subject = module.subject
                db.session.add(g.user)
                db.session.commit()
            return redirect(url_for('.index'))
        else:
            flash('There is no such module to edit')

    if request.method == 'GET':
        objectives = g.user.visible_objectives().all()
        objectives.sort(key=operator.methodcaller(
            "score"))  #DJG - isn't there a way of doing this within the order_by of the query

        return render_template('editmodule.html',
                               title=title,
                               form_header=form_header,
                               edit_id=id,
                               objectives=objectives,
                               module=module,
                               module_objectives=module_objectives,
                               edit_module_form=moduleform,
                               objectiveform=objectiveform)

    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        moduleform.module_objectives.choices = [(i, i) for i in moduleform.module_objectives.data]
        #Both material upload types are required in the moduleform definition so need to remove the redundant field now to prevent validation errors

        #if material_source == 'upload':           #DJG - need a way to define the global list of sources so value means the same thing as database definitions 
        #    del moduleform.material_youtube
        #elif material_source == 'youtube':
        #    del moduleform.material_upload              
        #if moduleform.material_type.data == 'course':
        #    del moduleform.material_upload
        #    del moduleform.material_youtube
        #import pdb; pdb.set_trace()
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
                select_list = moduleform.module_objectives.data
                if select_list:
                    objectives = g.user.visible_objectives().filter(Objective.name.in_(
                        select_list)).all()  #DJG - avoiding using the in_ operation when the list is empty as this is an inefficiency

                undefined_objectives = list(set(select_list) - set(obj.name for obj in
                                                                   objectives))  #DJG - Need to trap undefined objectives and return savedsucess as json if failed

                if undefined_objectives:  #DJG - code repeat of above, how to avoid this
                    is_are = 'is not already defined as an objetive' if len(
                        undefined_objectives) == 1 else 'are not already defined as objetives'
                    result['objectives'] = ["'" + "', '".join(undefined_objectives) + "' " + is_are]
                    return json.dumps(result)

                material_source = moduleform.material_source.data
                if module:
                    if module.material_source == material_source and material_source == "upload":
                        material_path = module.material_path

                if material_source == 'upload' and 'material' in request.files:  #DJG - Does flask-uploads automatically check against the allowed extention types and make the filename safe? Believe so.
                    material_path = lectures.save(request.files[
                        'material'])  #This saves the file and returns its name (including the folder)

                elif material_source == 'youtube' and moduleform.material_youtube.data:
                    material_path = moduleform.material_youtube.data
                    if not "?rel=0" in material_path:
                        material_path = material_path + "?rel=0"  #DJG - Add this text string on to stop youtube videos showing followon videos directly in the iframe


                if material_path:
                    proceed = True
                    result['material'] = [material_path]
                else:
                    result['material'] = ["No content provided"]
            else:  #DJG - method below can be improved now?!...
                unicode_list = request.form[
                    "course_modules"]  #DJG - the data sent by the ajax request has the list converted into a unicode text string with commas
                material_type = module.material_type
                python_list = filter(None, unicode_list.split(','))
                if python_list: course_modules = [Module.query.get(mod_id) for mod_id in
                                                  python_list]  #DJG - need some validation here to make sure modules exist and are not themselves courses etc.
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
                    module.modules = []  #DJG - need this to make the order of modules editable - or else need an association object in sqlalchamy to capture order as extra data of the many to many relationship
                    db.session.commit()
                    module.modules = course_modules
                    module.subtitles = moduleform.subtitles.data
                    module.easy_language = moduleform.easy_language.data
                    module.extension = moduleform.extension.data
                    module.for_teachers = moduleform.for_teachers.data
                    db.session.add(module)
                    db.session.commit()
                else:
                    module = Module.CreateModule(
                        name=moduleform.name.data,
                        description=moduleform.description.data,
                        notes=moduleform.notes.data,
                        author=g.user,
                        material_type=material_type,
                        material_source=material_source,
                        material_path=material_path,
                        subject=g.user.subject,
                        objectives=objectives,
                        subtitles=moduleform.subtitles.data,
                        easy_language=moduleform.easy_language.data,
                        extension=moduleform.extension.data,
                        for_teachers=moduleform.for_teachers.data
                    )

                result['savedsuccess'] = True
                result['module_id'] = module.id
                flash(material_type + " saved as " + module.name)

            return json.dumps(result)

        else:
            moduleform.errors['savedsuccess'] = False
            return json.dumps(moduleform.errors)


@main.route('/module/<int:id>')
@login_required
#DJG - Login should not be required just temporary to stop user_module tracking breaking - need guest user
def module(id):
    title = "CourseMe - Module"
    module = Module.query.get_or_404(id)
    g.user.subject_id = module.subject_id
    db.session.add(g.user)
    db.session.commit()
    messageform = forms.SendMessage()
    usermodule = UserModule.FindOrCreate(g.user.id, id)
    templates = {"Lecture": "lecture.html", "Course": "course.html"}

    return render_template(templates[module.material_type],
                           title=title,
                           messageform=messageform,
                           module=module,
                           usermodule=usermodule)


@main.route('/star/<int:id>')
@login_required
def starclick(id):
    module = Module.query.get_or_404(id)
    user = g.user

    usermodule = UserModule.FindOrCreate(user.id, module.id)

    usermodule.starred = not usermodule.starred
    db.session.add(usermodule)
    db.session.commit()

    return usermodule.as_json()


@main.route('/vote/<int:id>')
@login_required
def voteclick(id):
    module = Module.query.get_or_404(id)

    usermodule = UserModule.FindOrCreate(g.user.id, module.id)

    newVote = int(request.args.get("vote"))
    module.votes = module.votes - usermodule.vote + newVote  #DJG - Almost certainly a better way
    usermodule.vote = newVote

    db.session.add(usermodule)
    db.session.add(module)
    db.session.commit()

    return ""  #DJG - What is best return value when I don't care about the return result? Only thing I found that worked


@main.route('/add-module-to-course/<int:module_id>/<int:course_id>')
@login_required
def add_module_to_course(module_id, course_id):
    result = {'savedsuccess': False}
    if not g.user.subject:
        flash("You need to select what subject you are interested in")
        return redirect(url_for('.index'))

    if course_id == 0:
        course = Module.CreateModule(
            name="New Course",
            author=g.user,
            subject=g.user.subject,
            material_type="Course")
    else:
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
                    flash('You cannot add modules to a ' + course.material_type)
                elif course.subject_id != module.subject_id:
                    flash('You cannot add a ' + module.subject.name + ' module to a ' + course.subject.name + ' course')
                else:
                    course_modules = course.modules.all()
                    course_modules.append(module)
                    course.modules = course_modules
                    course.last_updated = datetime.utcnow()
                    db.session.commit()
                    result['savedsuccess'] = True
            else:
                flash('No Course identified with id ' + course_id)
    else:
        flash('No Module identified with id ' + module_id)

    return json.dumps(result)


@main.route('/course-enroll/<int:course_id>', methods=['POST'])
@login_required
def course_enroll(course_id):
    result = {}
    result['savedsuccess'] = False
    course = Module.query.get(course_id)

    if course:
        if course.material_type == "Course":
            usermodule = UserModule.FindOrCreate(g.user.id, course.id)
            usermodule.enrolled = not usermodule.enrolled
            db.session.commit()
            result['savedsuccess'] = True
            result['enrolled'] = usermodule.enrolled
        else:
            flash("Cannot enroll to " + course.material_type)
    else:
        flash('No Course identified with id ' + course_id)

    return json.dumps(result)


@main.route('/delete_module/<int:id>')
@login_required
def delete_module(id):
    result = {'savedsuccess': False}
    module = Module.query.get(id)

    if module:
        if module.author == g.user:
            module.delete()
            result['savedsuccess'] = True
        else:
            flash("You are not authorised to delete this " + module.material_type)
    else:
        flash('No Module identified with id ' + id)

    return json.dumps(result)


@main.route('/profile/<int:id>')
@login_required
def profile(id):
    profile = User.query.get(id)
    if not profile:
        flash("This user does not exist")
        return redirect(url_for('.profile', id=g.user.id))
    else:
        title = "CourseMe - Profile"
        permission = profile.permission(g.user)
        return render_template('user_profile.html',
                               title=title,
                               profile=profile,
                               permission=permission)


@main.route('/students')
@login_required
def students():
    title = "CourseMe - Students"
    return render_template('students.html',
                           title=title)


@main.route('/messages')
@login_required
def messages():
    title = "CourseMe - Messages"
    return render_template('messages.html',
                           title=title)


@main.route('/groups')
@login_required
def groups():
    title = "CourseMe - Groups"
    form = forms.EditGroup()
    return render_template(
        'groups.html',
        form=form,
        title=title
    )


@main.route('/group_get/<int:id>')
@login_required
def group_get(id):
    group = Group.query.get(id)
    if group:
        if group.creator == g.user:
            return json.dumps(group.as_dict())
        else:
            flash('You are not authorised to view this group')
            return json.dumps({'error': 'unauthorised'})
    else:
        flash('This group does not exist')
        return json.dumps({'error': 'not found'})


@main.route('/group_save', methods=['POST'])
@login_required
def group_save():
    form = forms.EditGroup()
    form.edit_group_members.choices = [(i, i) for i in
                                       form.edit_group_members.data]  #DJG - could put some actual validation here

    if form.validate():
        result = {}
        result['savedsuccess'] = False
        id = int(form.edit_group_id.data)
        #import pdb; pdb.set_trace()
        group_members = [User.user_by_email(e) for e in form.edit_group_members.data]
        if id > 0:
            group = Group.query.get(id)
            if group:
                if group.creator == g.user:
                    group.name = form.edit_group_name.data
                    group.members = group_members
                    db.session.add(group)
                    db.session.commit()
                    result['savedsuccess'] = True
                    flash('Group saved as ' + group.name)
                else:
                    flash('You are not authorised to edit this group')
                    result['error'] = "unauthorised"
            else:
                flash('This group does not exist')
                result['error'] = "not found"
        else:
            group = Group(
                name=form.edit_group_name.data,
                creator=g.user,
                members=group_members
            )
            db.session.add(group)
            db.session.commit()
            result['savedsuccess'] = True
            flash('New Group saved as ' + group.name)
        return json.dumps(result)
    else:
        form.errors['savedsuccess'] = False
        return json.dumps(form.errors)


@main.route('/group_delete/<int:id>')
@login_required
def group_delete(id):
    result = {}
    result['savedsuccess'] = False
    group = Group.query.get(id)
    if group:
        if group.creator == g.user:
            db.session.delete(group)
            db.session.commit()
            result['savedsuccess'] = True
        else:
            flash('You are not authorised to delete this group')
            result['error'] = "unauthorised"
    else:
        flash('This group does not exist')
        result['error'] = "not found"
    return json.dumps(result)


@main.route('/schemes')
@login_required
def schemes():
    title = "CourseMe - Schemes of Work"
    form = forms.EditScheme()
    return render_template(
        'schemes.html',
        form=form,
        title=title
    )


@main.route('/scheme_get/<int:id>')
@login_required
def scheme_get(id):
    scheme = SchemeOfWork.query.get(id)
    if scheme:
        if scheme.creator == g.user:
            return json.dumps(scheme.as_dict())
        else:
            flash('You are not authorised to view this scheme of work')
            return json.dumps({'error': 'unauthorised'})
    else:
        flash('This scheme of work does not exist')
        return json.dumps({'error': 'not found'})


@main.route('/scheme_save', methods=['POST'])
@login_required
def scheme_save():
    form = forms.EditScheme()
    form.edit_scheme_objectives.choices = [(i, i) for i in
                                           form.edit_scheme_objectives.data]  #DJG - could put some actual validation here

    if form.validate():
        result = {}
        result['savedsuccess'] = False
        id = int(form.edit_scheme_id.data)
        #import pdb; pdb.set_trace()
        scheme_objectives = [Objective.query.filter_by(name=o).one() for o in form.edit_scheme_objectives.data]
        if id > 0:
            scheme = SchemeOfWork.query.get(id)
            if scheme:
                if scheme.creator == g.user:
                    scheme.name = form.edit_scheme_name.data
                    scheme.objectives = scheme_objectives
                    db.session.add(scheme)
                    db.session.commit()
                    result['savedsuccess'] = True
                    flash('Scheme saved as ' + scheme.name)
                else:
                    flash('You are not authorised to edit this scheme of work')
                    result['error'] = "unauthorised"
            else:
                flash('This scheme of work does not exist')
                result['error'] = "not found"
        else:
            scheme = SchemeOfWork(
                name=form.edit_scheme_name.data,
                creator=g.user,
                objectives=scheme_objectives
            )
            db.session.add(scheme)
            db.session.commit()
            result['savedsuccess'] = True
            flash('New scheme of work saved as ' + scheme.name)
        return json.dumps(result)
    else:
        form.errors['savedsuccess'] = False
        return json.dumps(form.errors)


@main.route('/scheme_delete/<int:id>')
@login_required
def scheme_delete(id):
    result = {}
    result['savedsuccess'] = False
    scheme = SchemeOfWork.query.get(id)
    if scheme:
        if scheme.creator == g.user:
            db.session.delete(scheme)
            db.session.commit()
            result['savedsuccess'] = True
        else:
            flash('You are not authorised to delete this scheme of work')
            result['error'] = "unauthorised"
    else:
        flash('This scheme of work does not exist')
        result['error'] = "not found"
    return json.dumps(result)


@main.route('/restrict_modules_viewed/<int:user_id>/<int:institution_id>')
@login_required
def restrict_modules_viewed(user_id, institution_id):
    result = {}
    result['savedsuccess'] = False
    if user_id == g.user.id:
        if institution_id == 0:
            g.user.view_institution_only_id = 0
            db.session.add(g.user)
            db.session.commit()
            result['savedsuccess'] = True
        else:
            institution = Institution.query.get(institution_id)
            if institution:
                g.user.view_institution_only = institution
                db.session.add(g.user)
                db.session.commit()
                result['savedsuccess'] = True
            else:
                flash('Institution not found with id ' + institution_id)
                result["institution_error"] = True
    else:
        flash('You are not logged in as this user')
        result["user_error"] = True

    return json.dumps(result)


@main.route('/send_message', methods=['POST'])
@login_required
def send_message():
    form = forms.SendMessage()
    result = {}
    result['savedsuccess'] = False
    #import pdb; pdb.set_trace()
    if form.validate():
        #print 'message form submitted'
        #import pdb; pdb.set_trace()
        recommended_material = Module.query.get(form.recommended_material.data)
        if recommended_material:
            if form.message_type.data == "Individual":
                recipient = User.user_by_email(form.message_to.data)
                if recipient:
                    message = Message(
                        from_user=g.user,
                        to_user=recipient,
                        subject=form.message_subject.data,
                        body=form.message_body.data,
                        request_access=form.request_access.data,
                        recommended_material_id=recommended_material.id
                    )
                    db.session.add(message)
                    db.session.commit()
                    result['savedsuccess'] = True
                else:
                    result["message_to_unfound"] = form.message_to.data
            elif form.message_type.data == "Group":
                group = Group.query.filter_by(name=form.message_to.data, creator=g.user).one()
                if group:
                    group.message(
                        subject=form.message_subject.data,
                        body=form.message_body.data,
                        request_access=form.request_access.data,
                        recommended_material=recommended_material
                    )
                    result['savedsuccess'] = True
                else:
                    result["message_to"] = "Group of recipients not found"
            else:
                result["message_type"] = "Message type not recognised"
        else:
            result["recommended_material"] = "Module not found"

        return json.dumps(result)
    else:
        form.errors['savedsuccess'] = False
        return json.dumps(form.errors)


@main.route('/allow_access/<int:request_id>', methods=['POST'])
@login_required
def allow_access(request_id):
    result = {}
    request_from = User.query.get(request_id)
    if request_from:
        result['savedsuccess'] = g.user.allow_access(request_from)
    else:
        flash("Tutor not found")
        result['savedsuccess'] = False
    return json.dumps(result)


@main.route('/deny_access/<int:request_id>', methods=['POST'])
@login_required
def deny_access(request_id):
    result = {}
    request_from = User.query.get(request_id)
    if request_from:
        result['savedsuccess'] = g.user.deny_access(request_from)
    else:
        flash("Tutor not found")
        result['savedsuccess'] = False
    return json.dumps(result)


@main.route('/edit-question/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_question(id=0):
    title = "CourseMe - Questions"
    form = forms.EditQuestion()
    objectiveform = forms.EditObjective()
    objectiveform.edit_objective_topic.choices = Topic.TopicChoices(
        g.user)  #DJG - need to include this extra line everywhere to populate the objective topic choices. Can't do this in forms or models directy as no knowledge of tyhe session variable and so user in those places?
    question_objectives = []
    question = None
    #import pdb; pdb.set_trace()
    form_header = "Create new question:"
    if id > 0:
        question = Question.query.get(id)
        if question:
            if question.author_id != g.user.id:
                flash('You are not authorised to edit this question')
                return redirect(url_for('.questions'))
            elif request.method == 'GET':
                form_header = "Edit question:"
                g.user.subject_id = question.subject_id
                db.session.add(g.user)
                db.session.commit()
                form = forms.EditQuestion(
                    question=question.question,
                    answer=question.answer,
                    extension=question.extension
                )
                question_objectives = question.objectives
        else:
            flash('There is no such question to edit')
            return redirect(url_for('.questions'))

    if request.method == 'GET':
        objectives = g.user.visible_objectives().all()
        objectives.sort(key=operator.methodcaller(
            "score"))  #DJG - isn't there a way of doing this within the order_by of the query

        return render_template('edit_question.html',
                               title=title,
                               form_header=form_header,
                               form=form,
                               question_objectives=question_objectives,
                               objectiveform=objectiveform,
                               objectives=objectives,
                               edit_id=id)

    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        form.question_objectives.choices = [(i, i) for i in form.question_objectives.data]

        if form.validate():
            objectives = []
            result = {}
            result['savedsuccess'] = False
            proceed = False

            select_list = form.question_objectives.data
            if select_list: objectives = g.user.visible_objectives().filter(Objective.name.in_(
                select_list)).all()  #DJG - avoiding using the in_ operation when the list is empty as this is an inefficiency
            undefined_objectives = list(set(select_list) - set(obj.name for obj in
                                                               objectives))  #DJG - Need to trap undefined objectives and return savedsucess as json if failed

            if undefined_objectives:  #DJG - code repeat of above, how to avoid this
                is_are = 'is not already defined as an objetive' if len(
                    undefined_objectives) == 1 else 'are not already defined as objetives'
                result['objectives'] = ["'" + "', '".join(undefined_objectives) + "' " + is_are]
                return json.dumps(result)
            else:
                proceed = True

            if question and g.user.subject_id != question.subject_id:
                result['subject'] = [question.subject_id]
                proceed = False

            if proceed:
                if question:
                    question.question = form.question.data
                    question.answer = form.answer.data
                    question.objectives = objectives
                    question.extension = form.extension.data
                    question.visually_impaired = form.visually_impaired.data
                    question.last_updated = datetime.utcnow()
                    db.session.add(question)
                    db.session.commit()
                else:
                    question = Question.CreateQuestion(
                        question=form.question.data,
                        answer=form.answer.data,
                        subject=g.user.subject,
                        author=g.user,
                        objectives=objectives,
                        extension=form.extension.data,
                        visually_impaired=form.visually_impaired.data
                    )

                result['savedsuccess'] = True
                result['question_id'] = question.id
                flash("Question saved")

            return redirect(url_for('.questions'))

        else:
            form.errors['savedsuccess'] = False
            return json.dumps(form.errors)


@main.route('/delete-question/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_question(id=0):
    result = {}
    result['savedsuccess'] = False
    question = Question.query.get(id)
    if question:
        if question.author == g.user:
            db.session.delete(question)
            db.session.commit()
            result['savedsuccess'] = True
            return json.dumps(result)
        else:
            flash('You are not authorised to delete this question')
            return redirect(url_for('.questions'))
    else:
        flash('This question does not exist')
        return redirect(url_for('.questions'))


@main.route('/questions', methods=['GET'])
def questions():
    title = "CourseMe - Questions"
    if g.user.is_authenticated():
        questions = g.user.visible_questions().all()
        catalogue = [question.as_dict(g.user) for question in
                     questions]  #DJG - confused over best way to do this http://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
    else:
        questions = Question.query.all()
        catalogue = [question.as_dict() for question in
                     questions]  #DJG - confused over best way to do this http://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict

    return render_template('questions.html',
                           title=title,
                           questions=questions,
                           catalogue=json.dumps(catalogue)
    )


@main.route('/select-question/<int:id>', methods=['GET', 'POST'])
@login_required
def select_question(id=0):
    result = {}
    result['savedsuccess'] = False
    question = Question.query.get(id)
    if question:
        result['selected_class'] = g.user.toggle_select_question(question)
        result['savedsuccess'] = True
        return json.dumps(result)
    else:
        flash('This question does not exist')
        return redirect(url_for('.questions'))


@main.route('/questions-print', methods=['GET'])
@login_required
def questions_print():
    # return app.send_static_file('print_questions.html')
    title = "CourseMe - Questions"
    if g.user.is_authenticated():
        questions = g.user.questions_selected
        catalogue = [question.as_dict(g.user) for question in questions]  #DJG - confused over best way to do this http://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
    else:
        questions =[]
        catalogue = []
    return render_template('questions_print.html',
                           title=title,
                           questions=questions,
                           catalogue=json.dumps(catalogue)
    )


@main.route('/selected-questions', methods=['GET'])
@login_required
def selected_questions():
    questions = g.user.questions_selected
    catalogue = [question.as_dict() for question in questions]  #DJG - confused over best way to do this http://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
    return json.dumps(catalogue)


@main.route('/deselect-all-questions', methods=['GET'])
@login_required
def deselect_all_questions():
    g.user.questions_selected = []
    db.session.add(g.user)
    db.session.commit()
    return redirect(url_for('.questions'))


@main.route('/invitation/<email>')
@login_required
def invitation_email(email):
    send_email(email, 'Invitation email', 'mail/invitation_email', user=g.user)

@main.route('/angular', methods=['GET'])
def test_angular():
    title = "CourseMe - Angular"
    return render_template('test_angular.html',
                           title=title
    )
