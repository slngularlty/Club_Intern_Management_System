from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.db import mongo, hash_password, verify_password, get_resources, get_meetings, get_intern_by_username
from bson.objectid import ObjectId
from functools import wraps

bp = Blueprint('intern', __name__, url_prefix='/intern')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('intern_username'):
            return f(*args, **kwargs)
        elif session.get('admin_logged_in'):
            flash('Access Denied: You must be an Intern to view this page. Please log out of your Admin account first.', 'danger')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('intern.login'))
    return decorated_function

@bp.route('/dashboard')
@login_required
def intern_dashboard():
    intern_username = session.get('intern_username')
    if not intern_username:
        flash('Intern session expired or invalid. Please log in again.', 'danger')
        return redirect(url_for('intern.login'))

    intern = mongo.db.interns.find_one({'username': intern_username})
    if not intern:
        flash('Intern profile not found. Please contact support.', 'danger')
        session.clear()
        return redirect(url_for('intern.login'))

    recent_tasks = []
    if 'task' in intern:
        recent_tasks.append(intern['task'])

    # Team members (other interns in the same team) - DO NOT DISPLAY USERNAME
    team_members = list(mongo.db.interns.find({'team': intern.get('team', ''), 'username': {'$ne': intern_username}}))

    resources = get_resources()
    meetings = get_meetings()
    return render_template('intern_dashboard.html', intern=intern, recent_tasks=recent_tasks, team_members=team_members, resources=resources, meetings=meetings)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('intern_username'):
        return redirect(url_for('intern.intern_dashboard'))

    if session.get('admin_logged_in'):
        flash('You are currently logged in as an Admin. Please log out first to access the Intern login.', 'warning')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        intern = get_intern_by_username(username)

        if intern and 'password' in intern and verify_password(intern['password'], password):
            session.clear()
            session['intern_logged_in'] = True
            session['intern_username'] = username
            session['intern_id'] = str(intern['_id'])
            session['intern_name'] = intern['name']
            flash('Logged in successfully as Intern!', 'success')
            return redirect(url_for('intern.intern_dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('intern_username', None)
    session.pop('intern_name', None)
    session.pop('intern_logged_in', None)
    session.pop('intern_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home.home'))