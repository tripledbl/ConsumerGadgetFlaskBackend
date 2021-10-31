from flask import Blueprint
from flask import jsonify
from database import mongo_client

userRoutes = Blueprint('userRoutes', __name__)

@userRoutes.route('/users')
def users():
    return 'hello from users'

@userRoutes.route('/add_user')
def add_user():
    user_collection = mongo_client.db.Users
    user_collection.insert_one({'Name': "haha", 'Username': "lmao"})
    return jsonify(message="success")