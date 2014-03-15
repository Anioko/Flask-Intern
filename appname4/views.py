# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, session, request, g, send_from_directory, send_file, Response, abort, safe_join, make_response
from flask.ext.login import login_user, logout_user, current_user, login_required
from sqlalchemy import exc
from appname4 import app, db, lm
from forms import LoginForm, SignupForm, ModifyForm, PasswordForm, CompanyForm
from models import User, Company, Intern
from functools import wraps
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField
#import os, glob, formic, urllib2, base64, json, zlib
from werkzeug.security import generate_password_hash, check_password_hash



def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        role = g.user.role
        if role not in [1, 2]:
            flash('Invalid permissions.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@lm.user_loader
def load_user(user_id):
    user_id = User.query.get(user_id)
    return user_id

@app.before_request
def before_request():
    g.user = current_user
    
#Internal Admin account setup
@app.route('/setup', methods = ['GET', 'POST'])
def setup():
    """Setup page, only accessible if no users exist"""
    # Try if database exists
    try:
        # If no user found in database, show form
        if db.session.query(User).count() < 1:
            form = SignupForm()
            # Passed form validation? continue
            if form.validate_on_submit():
                # Create user object and add it to database
                user = User(username = form.username.data, password = generate_password_hash(form.password.data), role = 3)
                db.session.add(user)
                db.session.commit()
                flash('Account created! You are now logged in!')
                # Log new user in
                login_user(user)
                return redirect(url_for('index'))
            return render_template('add.html', form = form)
        else:
            flash('Setup already completed.')
            return redirect(url_for('index'))
    # If not, let's create the database:
    except exc.OperationalError:
        db.create_all()
        return redirect(url_for('setup'))


@app.route('/public')
def public_index():
    return render_template('public/index.html')


@app.route('/')
@app.route('/index')
def index():
    return render_template('public/index.html')


@app.route('/positions')
@app.route('/position/')
def public_positions():
    needs = Company.query.all()
    return render_template('public/positions.html', needs=needs)



@app.route('/login')
def login():
    """Login page. Checking of password in this method"""
    # Already authenticated? gtfo
    if g.user is not None and g.user.is_authenticated():
        flash('Already logged in.')
        return redirect(url_for('company_index'))
    return render_template('public/login.html')


@app.route('/signup/')
@app.route('/signup')
def public_signup():
    return render_template('public/signup.html')

        
    

@app.route('/admin/<what>/<int:who>')
@app.route('/admin/')
#@admin_required
def internal_admin(what = None, who = None):
    """Admin area with moderation functions"""
    if who == 1:
        flash('Deleting of admin account is not possible.')
        return redirect(url_for('school_admin'))
    if what is None and who is None:
        users = User.query.filter_by(role = 0).all()
        admins = User.query.filter_by(role = 2).all()
        return render_template('admin.html', users = users, admins=admins)
    else:
        user = User.query.filter_by(id = who).first()
        name = user.username
        if what == 'delete':
            db.session.delete(user)
            message = 'User {!s} deleted.'.format(name)
        elif what == 'promote':
            user.role = 2
            message = 'User {!s} promoted to moderator.'.format(name)
        elif what == 'demote':
            user.role = 0
            message = 'User {!s} demoted to normal user.'.format(name)
        else:
            return redirect(url_for('internal_admin'))
        db.session.commit()
        flash(message)
    return redirect(url_for('internal_admin'))


###########Company's views Begins#############


@app.route('/company/signup/', methods=['GET', 'POST'])

def company_signup():
    """Provide HTML form to adda new student record."""
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(username = form.username.data, password = generate_password_hash(form.password.data), role = 3)
        db.session.add(user)
        db.session.commit()
        # Success. Send the user back to the full appointment list.
        return redirect(url_for('company_index'))
    # Either first load or validation error at this point.
    return render_template('company/signup.html', form=form)




@app.route('/company/login', methods = ['GET', 'POST'])
def company_login():
    """Login page. Checking of password in this method"""
    # Already authenticated? gtfo
    if g.user is not None and g.user.is_authenticated():
        flash('Already logged in.')
        return redirect(url_for('company_index'))
    form = LoginForm()
    # Passed form validation? let's roll
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user = form.username.data
        user_data = User.query.filter_by(username = user, role = 3).first()
        # User exists
        if user_data:
            # Password matches
            if check_password_hash(user_data.password, form.password.data):
                # Ticket 'remember me'?
                if 'remember_me' in session:
                    remember_me = session['remember_me']
                    session.pop('remember_me', None)
                # All good, let's log user in
                login_user(user_data, remember = remember_me)
                return redirect(request.args.get('next') or url_for('company_index'))
            else:
                flash('Invalid username or password')
        else:
            flash('Invalid username or password')
    return render_template('company/login.html', form = form)




##
##@app.route('/company/profile', methods = ['GET', 'POST'])
##@login_required
##def company_profile():
##    """Profile page with ability to change password"""
##    form = PasswordForm()
##    # Form submitted?
##    if form.validate_on_submit():
##        # Fetch current user's data
##        user_data = User.query.filter_by(id = g.user.id).first()
##        # Check if old password was correct
##        if check_password_hash(user_data.password, form.password.data):
##            # Generate new password
##            user_data.password = generate_password_hash(form.newpassword.data)
##            # Done, commit to database
##            db.session.commit()
##            flash('Password changed!')
##            return redirect(url_for('company_profile'))
##    return render_template('company/profile.html', form = form)
##






@app.route('/company/vacancies')
#@login_required
def company_list():
    
    # Query.
    needs = (db.session.query(Company)
             .filter_by(user_id=current_user.id)
             .order_by(Company.start.asc()).all())
    return render_template('company/index.html', needs=needs)

@app.route('/company/<int:company_id>/')
@login_required
def company_detail(company_id):
    """Provide HTML page with all details on a given company."""
    # Query: get Company object by ID.
    need = db.session.query(Company).get(company_id)
    if need is None or need.user_id != current_user.id:
        # Abort with Not Found.
        abort(404)
    return render_template('company/detail.html', need=need)


@app.route('/company')
@app.route('/company/index')
@login_required
def company_index():
    
    # Query.
    #needs = Company.query.all()
    needs = Company.query.all()
    return render_template('company/index.html', needs=needs)

@app.route('/company/create/', methods=['GET', 'POST'])
@login_required
def add_position():
    """Provide HTML form to adda new student record."""
    form = CompanyForm(request.form)
    if request.method == 'POST' and form.validate():
        need = Company()
        db.session.add(need)
        db.session.commit()
        flash('Account created! Check www.Intern.ly/position to see it. Thank you! ')
        # Success. Send the user back to the full appointment list.
        return redirect(url_for('company_index'))
    # Either first load or validation error at this point.
    return render_template('company/add.html', form=form)

  




##
##@app.route('/company/<int:company_id>/edit/', methods=['GET', 'POST'])
##def company_edit(company_id):
##  """Provide HTML form to edit a given need."""
##  need = db.session.query(Company).get(company_id)
##  if need is None:
##    abort(404)
##  if need.user_id != current_user.id:
##    abort(403)
##  form = CompanyForm(request.form, need)
##  if request.method == 'POST' and form.validate():
##    form.populate_obj(need)
##    db.session.commit()
##    # Success. Send the user back to the detail view of that appointment.
##    return redirect(url_for('company_detail', company_id=need.id))
##  return render_template('company/edit.html', form=form)
##
##
##@app.route('/company/<int:company_id>/delete/', methods=['DELETE'])
##def company_delete(company_id):
##  """Delete a record using HTTP DELETE, respond with JSON for JavaScript."""
##  need = db.session.query(Company).get(company_id)
##  if deal is None:
##    # Abort with simple response indicating appointment not found.
##    response = jsonify({'status': 'Not Found'})
##    response.status_code = 404
##    return response
##  if need.user_id != current_user.id:
##    # Abort with simple response indicating forbidden.
##    response = jsonify({'status': 'Forbidden'})
##    response.status_code = 403
##    return response
##  db.session.delete(company)
##  db.session.commit()
##  return jsonify({'status': 'OK'})	


@app.route('/company/logout')
def company_logout():
    """Just log out the user, no fancy stuff"""
    logout_user()
    
    return redirect(url_for('company_login'))




#########Company Views Ends ################



#######Signup views for School#######
@app.route('/school/signup/', methods = ['GET', 'POST'])  
@app.route('/school/signup', methods = ['GET', 'POST'])
def signup():
    """Register page. Only admin/moderator can create new users"""
    form = SignupForm()
    # Form validation passed? Add new user.
    if form.validate_on_submit():
        user = User(username = form.username.data, password = generate_password_hash(form.password.data), role = 1)
        db.session.add(user)
        db.session.commit()
        flash('Account created!')
        login_user(user)
        return redirect(url_for('school_index'))
    return render_template('school/signup.html', form = form)


@app.route('/school/login/', methods = ['GET', 'POST'])
@app.route('/school/login', methods = ['GET', 'POST'])
def school_login():
    """Login page. Checking of password in this method"""
    # Already authenticated? gtfo
    if g.user is not None and g.user.is_authenticated():
        flash('Already logged in.')
        return redirect(url_for('school_index'))
    form = LoginForm()
    # Passed form validation? let's roll
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user = form.username.data
        user_data = User.query.filter_by(username = user, role = 1).first()
        # User exists
        if user_data:
            # Password matches
            if check_password_hash(user_data.password, form.password.data):
                # Ticket 'remember me'?
                if 'remember_me' in session:
                    remember_me = session['remember_me']
                    session.pop('remember_me', None)
                # All good, let's log user in
                login_user(user_data, remember = remember_me)
                return redirect(request.args.get('next') or url_for('school_index'))
            else:
                flash('Invalid username or password')
        else:
            flash('Invalid username or password')
    return render_template('school/login.html', form = form)


@app.route('/school')
@app.route('/school/index')
@login_required
def school_index():
    return render_template('school/index.html')




@app.route('/school/create/', methods=['GET', 'POST'])
@login_required
def add_student():
    """Provide HTML form to adda new student record."""
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(username = form.username.data, password = generate_password_hash(form.password.data), role = 0)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please send the student you added the password. Thank you! ')
        # Success. Send the user back to the full appointment list.
        return redirect(url_for('school_index'))
    # Either first load or validation error at this point.
    return render_template('school/add.html', form=form)


@app.route('/school/profile', methods = ['GET', 'POST'])
@admin_required
def school_profile():
    """Profile page with ability to change password"""
    form = PasswordForm()
    # Form submitted?
    if form.validate_on_submit():
        # Fetch current user's data
        user_data = User.query.filter_by(id = g.user.id).first()
        # Check if old password was correct
        if check_password_hash(user_data.password, form.password.data):
            # Generate new password
            user_data.password = generate_password_hash(form.newpassword.data)
            # Done, commit to database
            db.session.commit()
            flash('Password changed!')
            return redirect(url_for('school_index'))
    return render_template('school/profile.html', form = form)

#######################Some issues here. I want to display only students that are added by a particular school. Right now it is not doing that. Revision needed





@app.route('/school/logout')
def school_logout():
    """Just log out the user, no fancy stuff"""
    logout_user()
    
    return redirect(url_for('school_login'))




########Beginning of Intern Views########

@app.route('/intern/signup/', methods = ['GET', 'POST'])  
@app.route('/intern/signup', methods = ['GET', 'POST'])
def intern_signup():
    """Register page """
    form = SignupForm()
    # Form validation passed? Add new user.
    if form.validate_on_submit():
        user = User(username = form.username.data, password = generate_password_hash(form.password.data), role = 0)
        db.session.add(user)
        db.session.commit()
        flash('Account created!')
        #login_user(user)
        return redirect(url_for('intern_login'))
    return render_template('intern/signup.html', form = form)

@app.route('/intern/login', methods = ['GET', 'POST'])
def intern_login():
    """Login page. Checking of password in this method"""
    # Already authenticated? gtfo
    if g.user is not None and g.user.is_authenticated():
        flash('Already logged in.')
        return redirect(url_for('intern_index'))
    form = LoginForm()
    # Passed form validation? let's roll
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user = form.username.data
        user_data = User.query.filter_by(username = user, role = 0).first()
        # User exists
        if user_data:
            # Password matches
            if check_password_hash(user_data.password, form.password.data):
                # Ticket 'remember me'?
                if 'remember_me' in session:
                    remember_me = session['remember_me']
                    session.pop('remember_me', None)
                # All good, let's log user in
                login_user(user_data, remember = remember_me)
                return redirect(request.args.get('next') or url_for('intern_index'))
            else:
                flash('Invalid username or password')
        else:
            flash('Invalid username or password')
    return render_template('intern/login.html', form = form)

@app.route('/intern')
@app.route('/intern/index')
@login_required
def intern_index():
    needs = Company.query.all()
    return render_template('intern/index.html', needs=needs)





@app.route('/intern/profile', methods = ['GET', 'POST'])
@login_required
def intern_profile():
    """Profile page with ability to change password"""
    form = PasswordForm()
    # Form submitted?
    if form.validate_on_submit():
        # Fetch current user's data
        user_data = User.query.filter_by(id = g.user.id).first()
        # Check if old password was correct
        if check_password_hash(user_data.password, form.password.data):
            # Generate new password
            user_data.password = generate_password_hash(form.newpassword.data)
            # Done, commit to database
            db.session.commit()
            flash('Password changed!')
            return redirect(url_for('intern_profile'))
    return render_template('intern/profile.html', form = form)

@app.route('/intern/logout')
def intern_logout():
    """Just log out the user, no fancy stuff"""
    logout_user()
    
    return redirect(url_for('intern_login'))


