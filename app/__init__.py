from flask import Flask
from .models.db import init_db
from .routes import admin, intern, home

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    init_db(app)

    app.register_blueprint(home.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(intern.bp)

    return app