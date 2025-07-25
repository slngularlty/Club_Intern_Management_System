from flask import Flask
from .models.db import init_db
from .routes import admin, intern, home
import os 

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get('FLASK_SECRET_KEY')
    app.config["MONGO_URI"] = os.environ.get('MONGO_URI')

    init_db(app)

    app.register_blueprint(home.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(intern.bp)

    return app