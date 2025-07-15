from flask import Flask
from .models.db import init_db
from .routes import admin, intern, home  # Import home blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    init_db(app)

    app.register_blueprint(home.bp)  # Home page at '/'
    app.register_blueprint(admin.bp) # Admin routes at '/admin'
    app.register_blueprint(intern.bp) # Intern routes at '/intern'

    return app
