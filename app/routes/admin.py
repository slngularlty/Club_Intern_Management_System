from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.db import mongo, get_resources, add_resource, delete_resource, get_meetings, add_meeting, delete_meeting
from bson.objectid import ObjectId
from functools import wraps
import os
import json

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

ADMIN_CREDENTIALS_FILE = 'admin_credentials.json'
def get_admin_credentials():
    if os.path.exists(ADMIN_CREDENTIALS_FILE):
        with open(ADMIN_CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return {'username': 'admin', 'password': 'admin123'}
def set_admin_credentials(username, password):
    with open(ADMIN_CREDENTIALS_FILE, 'w') as f:
        json.dump({'username': username, 'password': password}, f)

@bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    creds = get_admin_credentials()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == creds['username'] and password == creds['password']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    return render_template('admin_login.html')

@bp.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))

@bp.route('/change_credentials', methods=['GET', 'POST'])
@admin_login_required
def change_credentials():
    creds = get_admin_credentials()
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        set_admin_credentials(new_username, new_password)
        flash('Admin credentials updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('change_admin_credentials.html', username=creds['username'])

@bp.route('/')
@admin_login_required
def dashboard():
    interns = list(mongo.db.interns.find())
    return render_template('admin_dashboard.html', interns=interns)

@bp.route('/add', methods=['POST'])
@admin_login_required
def add_intern():
    name = request.form['name']
    team = request.form['team']
    task = request.form['task']
    mongo.db.interns.insert_one({'name': name, 'team': team, 'task': task})
    return redirect(url_for('admin.dashboard'))

@bp.route('/delete/<id>')
@admin_login_required
def delete_intern(id):
    mongo.db.interns.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('admin.dashboard'))

@bp.route('/resources_meetings', methods=['GET', 'POST'])
@admin_login_required
def resources_meetings():
    # Handle add resource
    if request.method == 'POST' and request.form.get('form_type') == 'resource':
        add_resource({
            'title': request.form['title'],
            'description': request.form['description'],
            'link': request.form['link'],
            'category': request.form.get('category', '')
        })
    # Handle add meeting
    if request.method == 'POST' and request.form.get('form_type') == 'meeting':
        add_meeting({
            'title': request.form['title'],
            'description': request.form['description'],
            'datetime': request.form['datetime'],
            'link': request.form['link']
        })
    resources = get_resources()
    meetings = get_meetings()
    return render_template('admin_resources_meetings.html', resources=resources, meetings=meetings)

@bp.route('/delete_resource/<id>')
@admin_login_required
def delete_resource_route(id):
    delete_resource(ObjectId(id))
    return redirect(url_for('admin.resources_meetings'))

@bp.route('/delete_meeting/<id>')
@admin_login_required
def delete_meeting_route(id):
    delete_meeting(ObjectId(id))
    return redirect(url_for('admin.resources_meetings'))
