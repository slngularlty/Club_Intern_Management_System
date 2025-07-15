from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hash):
    return check_password_hash(hash, password)

# Resource helpers
def get_resources():
    return list(mongo.db.resources.find())
def add_resource(resource):
    return mongo.db.resources.insert_one(resource)
def update_resource(resource_id, update):
    return mongo.db.resources.update_one({'_id': resource_id}, {'$set': update})
def delete_resource(resource_id):
    return mongo.db.resources.delete_one({'_id': resource_id})

# Meeting helpers
def get_meetings():
    return list(mongo.db.meetings.find())
def add_meeting(meeting):
    return mongo.db.meetings.insert_one(meeting)
def update_meeting(meeting_id, update):
    return mongo.db.meetings.update_one({'_id': meeting_id}, {'$set': update})
def delete_meeting(meeting_id):
    return mongo.db.meetings.delete_one({'_id': meeting_id})
