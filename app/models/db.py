from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)

def hash_password(password):
    return generate_password_hash(password)

def verify_password(stored_hash, provided_password):
    return check_password_hash(stored_hash, provided_password)

def find_admin_by_username(username):
    return mongo.db.admins.find_one({"username": username})

def update_admin_profile(current_username, new_username=None, new_password=None):

    update_fields = {}
    if new_username:
        update_fields["username"] = new_username
    if new_password:
        update_fields["password"] = hash_password(new_password)

    if update_fields:
        mongo.db.admins.update_one(
            {"username": current_username},
            {"$set": update_fields}
        )
        return True
    return False

def create_initial_admin(username, password):
    if mongo.db.admins.count_documents({}) == 0:
        hashed_password = hash_password(password)
        mongo.db.admins.insert_one({
            "username": username,
            "password": hashed_password
        })
        print(f"Initial admin '{username}' created in the database.")
        return True
    return False

def get_interns():
    return list(mongo.db.interns.find())

def add_intern(intern_data):
    if 'password' in intern_data and intern_data['password']:
        intern_data['password'] = hash_password(intern_data['password'])
    mongo.db.interns.insert_one(intern_data)

def delete_intern(intern_id):
    mongo.db.interns.delete_one({'_id': intern_id})

def get_intern_by_username(username):
    intern = mongo.db.interns.find_one({"username": username})
    if intern:
        intern['_id'] = str(intern['_id'])
    return intern

def get_resources():
    return list(mongo.db.resources.find())

def add_resource(resource_data):
    mongo.db.resources.insert_one(resource_data)

def delete_resource(resource_id):
    mongo.db.resources.delete_one({'_id': resource_id})

def get_meetings():
    return list(mongo.db.meetings.find())

def add_meeting(meeting_data):
    mongo.db.meetings.insert_one(meeting_data)

def delete_meeting(meeting_id):
    mongo.db.meetings.delete_one({'_id': meeting_id})