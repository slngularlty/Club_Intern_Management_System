from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models.db import mongo
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId

bp = Blueprint('home', __name__)

# --- Password Helper Function ---
def check_password(hashed_password, password):
    """Checks a password against a hashed password."""
    return check_password_hash(hashed_password, password)
# ---------------------------------------------------

@bp.route('/')
def home():
    # If Admin is logged in, redirect to Admin Dashboard
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard')) # Assuming 'admin.dashboard' is correct

    # If Intern is logged in, redirect to Intern Dashboard
    if session.get('intern_username'):
        # Redirect to intern dashboard (now without 'name' in URL)
        return redirect(url_for('intern.intern_dashboard'))

    # If neither Admin nor Intern is logged in, render the regular home page
    interns = list(mongo.db.interns.find())

    # Team overview: count interns per team
    team_overview = {}
    for intern in interns:
        team = intern.get('team', 'Unknown')
        team_overview[team] = team_overview.get(team, 0) + 1

    # Recent tasks: get last 5 unique tasks
    recent_tasks = []
    seen_tasks = set()
    for intern in interns:
        task = intern.get('task')
        if task and task not in seen_tasks:
            recent_tasks.append({'name': intern.get('name'), 'task': task})
            seen_tasks.add(task)
        if len(recent_tasks) >= 5:
            break

    # When accessing the root '/', no specific intern details are shown initially
    # No 'selected_intern_id' needed here anymore since details are client-side only
    return render_template('home.html', interns=interns, team_overview=team_overview, recent_tasks=recent_tasks, session=session)


@bp.route('/intern_login', methods=['GET', 'POST'])
def intern_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        intern = mongo.db.interns.find_one({'username': username})

        if intern and 'password' in intern and check_password(intern['password'], password):
            session.clear() # Clear previous session data (e.g., if admin was logged in)
            session['intern_logged_in'] = True
            session['intern_username'] = username
            session['intern_id'] = str(intern['_id'])
            session['intern_name'] = intern.get('name') # Store name for display purposes
            flash('Logged in successfully as Intern!', 'success')
            return redirect(url_for('intern.intern_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('home.intern_login')) # Keep on login page for re-attempt
    return render_template('login.html')