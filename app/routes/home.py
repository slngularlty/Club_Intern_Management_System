from flask import Blueprint, render_template
from app.models.db import mongo

bp = Blueprint('home', __name__)

@bp.route('/')
def home():
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
    return render_template('home.html', interns=interns, team_overview=team_overview, recent_tasks=recent_tasks)
