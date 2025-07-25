from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from app.models.db import mongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Password Helper Functions ---
def generate_password(password):
    """Hashes the given password."""
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """Checks a password against a hashed password."""
    return check_password_hash(hashed_password, password)
# ---------------------------------------------------

# Login Required Decorator
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Login Route
@bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_user = mongo.db.admins.find_one({'username': username})

        if admin_user and check_password(admin_user['password'], password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Logged in successfully as Admin!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin username or password. Please try again.', 'danger')
            return render_template('admin_login.html')
    return render_template('admin_login.html')

# Admin Logout Route
@bp.route('/logout')
@admin_login_required
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home.home'))

# Admin Dashboard
@bp.route('/dashboard')
@admin_login_required
def dashboard():
    interns = list(mongo.db.interns.find())
    return render_template('admin_dashboard.html', interns=interns)

# Add Intern (from modal)
@bp.route('/add_intern', methods=['POST'])
@admin_login_required
def add_intern():
    name = request.form['name']
    team = request.form['team']
    task = request.form['task']
    username = request.form.get('username')
    password = request.form.get('password')

    intern_data = {'name': name, 'team': team, 'task': task}

    if username:
        if mongo.db.interns.find_one({'username': username}):
            flash(f'Error: Username "{username}" already exists. Please choose a different one.', 'danger')
            return redirect(url_for('admin.dashboard'))
        intern_data['username'] = username
        if password:
            intern_data['password'] = generate_password(password)
        else:
            flash('Error: Username provided without a password.', 'danger')
            return redirect(url_for('admin.dashboard'))
    elif password:
        flash('Error: Password provided without a username.', 'danger')
        return redirect(url_for('admin.dashboard'))

    mongo.db.interns.insert_one(intern_data)
    flash('Intern added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

# Edit Intern (Admin Dashboard)
@bp.route('/edit_intern/<intern_id>', methods=['POST'])
@admin_login_required
def edit_intern_admin(intern_id):
    name = request.form['name']
    team = request.form['team']
    task = request.form['task']
    username = request.form.get('username')
    password = request.form.get('password')

    update_data = {
        'name': name,
        'team': team,
        'task': task
    }

    # Only update username if provided and changed AND not already taken
    if username:
        existing_intern_with_username = mongo.db.interns.find_one({
            'username': username,
            '_id': {'$ne': ObjectId(intern_id)}
        })
        if existing_intern_with_username:
            flash(f'Error: Username "{username}" already taken by another intern.', 'danger')
            return redirect(url_for('admin.dashboard'))
        update_data['username'] = username
    else: # If username field is left blank, remove username from intern's document
        update_data['$unset'] = {'username': ''}


    if password:
        update_data['password'] = generate_password(password)

    # Use $set and $unset correctly
    if '$unset' in update_data:
        mongo.db.interns.update_one({'_id': ObjectId(intern_id)}, {'$set': update_data, '$unset': update_data['$unset']})
    else:
        mongo.db.interns.update_one({'_id': ObjectId(intern_id)}, {'$set': update_data})

    flash('Intern updated successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


# Delete Intern
@bp.route('/delete_intern/<id>')
@admin_login_required
def delete_intern(id):
    mongo.db.interns.delete_one({'_id': ObjectId(id)})
    flash('Intern deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

# Resources & Meetings Page (Now handles POST for add via modals)
@bp.route('/resources_meetings', methods=['GET', 'POST'])
@admin_login_required
def resources_meetings():
    if request.method == 'POST':
        form_type = request.form['form_type']
        if form_type == 'resource':
            title = request.form['title']
            description = request.form['description']
            link = request.form['link']
            category = request.form.get('category')
            mongo.db.resources.insert_one({'title': title, 'description': description, 'link': link, 'category': category})
            flash('Resource added successfully!', 'success')
        elif form_type == 'meeting':
            title = request.form['title']
            description = request.form['description']
            datetime_str = request.form['datetime']
            link = request.form['link']
            mongo.db.meetings.insert_one({'title': title, 'description': description, 'datetime': datetime_str, 'link': link})
            flash('Meeting added successfully!', 'success')
        return redirect(url_for('admin.resources_meetings'))

    resources = list(mongo.db.resources.find())
    meetings = list(mongo.db.meetings.find())
    return render_template('admin_resources_meetings.html', resources=resources, meetings=meetings)

# Edit Resource
@bp.route('/edit_resource/<resource_id>', methods=['POST'])
@admin_login_required
def edit_resource(resource_id):
    title = request.form['title']
    description = request.form['description']
    link = request.form['link']
    category = request.form.get('category')

    update_data = {
        'title': title,
        'description': description,
        'link': link,
        'category': category
    }
    mongo.db.resources.update_one({'_id': ObjectId(resource_id)}, {'$set': update_data})
    flash('Resource updated successfully!', 'success')
    return redirect(url_for('admin.resources_meetings'))

# Edit Meeting
@bp.route('/edit_meeting/<meeting_id>', methods=['POST'])
@admin_login_required
def edit_meeting(meeting_id):
    title = request.form['title']
    description = request.form['description']
    datetime_str = request.form['datetime']
    link = request.form['link']

    update_data = {
        'title': title,
        'description': description,
        'datetime': datetime_str,
        'link': link
    }
    mongo.db.meetings.update_one({'_id': ObjectId(meeting_id)}, {'$set': update_data})
    flash('Meeting updated successfully!', 'success')
    return redirect(url_for('admin.resources_meetings'))


# Delete Resource
@bp.route('/delete_resource/<id>')
@admin_login_required
def delete_resource_route(id):
    mongo.db.resources.delete_one({'_id': ObjectId(id)})
    flash('Resource deleted successfully!', 'success')
    return redirect(url_for('admin.resources_meetings'))

# Delete Meeting
@bp.route('/delete_meeting/<id>')
@admin_login_required
def delete_meeting_route(id):
    mongo.db.meetings.delete_one({'_id': ObjectId(id)})
    flash('Meeting deleted successfully!', 'success')
    return redirect(url_for('admin.resources_meetings'))

# Change Admin Credentials
@bp.route('/change_credentials', methods=['GET', 'POST'])
@admin_login_required
def change_admin_credentials():
    admin_user = mongo.db.admins.find_one({'username': session['admin_username']})

    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        update_data = {}
        if new_username and new_username != admin_user['username']:
            if mongo.db.admins.find_one({'username': new_username}):
                flash('Error: New username already exists.', 'danger')
                return redirect(url_for('admin.change_admin_credentials'))
            update_data['username'] = new_username

        if new_password:
            if new_password != confirm_new_password:
                flash('Error: New password and confirmation do not match.', 'danger')
                return redirect(url_for('admin.change_admin_credentials'))
            update_data['password'] = generate_password(new_password)

        if update_data:
            mongo.db.admins.update_one({'_id': admin_user['_id']}, {'$set': update_data})

            if 'username' in update_data:
                session['admin_username'] = update_data['username']
            flash('Credentials updated successfully!', 'success')
        else:
            flash('No changes were submitted.', 'info')

        return redirect(url_for('admin.change_admin_credentials'))

    return render_template('change_admin_credentials.html')