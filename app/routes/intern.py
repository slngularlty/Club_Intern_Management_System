from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.db import mongo, hash_password, verify_password, get_resources, get_meetings
from bson.objectid import ObjectId
from functools import wraps

bp = Blueprint('intern', __name__, url_prefix='/intern')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'intern_username' not in session:
            # Try to redirect to the intern dashboard if intern_name is in session
            intern_name = session.get('intern_name')
            if intern_name:
                return redirect(url_for('intern.intern_dashboard', name=intern_name))
            else:
                return redirect(url_for('home.home'))  # fallback if no intern_name
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/<name>')
@login_required
def intern_dashboard(name):
    intern = mongo.db.interns.find_one({'name': name})
    # Recent tasks for this intern (if there is a history, else just current task)
    recent_tasks = []
    if 'task' in intern:
        recent_tasks.append(intern['task'])
    # Team members (other interns in the same team)
    team_members = list(mongo.db.interns.find({'team': intern.get('team', ''), 'name': {'$ne': name}}))
    resources = get_resources()
    meetings = get_meetings()
    return render_template('intern_dashboard.html', intern=intern, recent_tasks=recent_tasks, team_members=team_members, resources=resources, meetings=meetings)

@bp.route('/edit/<name>', methods=['POST'])
@login_required
def edit_intern(name):
    new_name = request.form['name']
    team = request.form['team']
    task = request.form['task']
    update_fields = {'name': new_name, 'team': team, 'task': task}
    username = request.form.get('username')
    password = request.form.get('password')
    if username:
        update_fields['username'] = username
    if password:
        update_fields['password'] = hash_password(password)
    mongo.db.interns.update_one({'name': name}, {'$set': update_fields})
    return redirect(url_for('intern.intern_dashboard', name=new_name))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        intern = mongo.db.interns.find_one({'username': username})
        if intern and 'password' in intern and verify_password(password, intern['password']):
            session['intern_username'] = username
            session['intern_name'] = intern['name']
            return redirect(url_for('intern.intern_dashboard', name=intern['name']))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('intern_username', None)
    session.pop('intern_name', None)
    return redirect(url_for('home.home'))
