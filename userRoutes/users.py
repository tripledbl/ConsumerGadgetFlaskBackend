from flask import Blueprint
from flask import jsonify
from database import mongo_client

userRoutes = Blueprint('userRoutes', __name__)

@userRoutes.route('/user/<string:name>', methods=['POST'])
def user(name):
    user_collection = mongo_client.db.Users
    user_collection.insert_one({'Name': name, 'Username': "lmao"})
    return jsonify(message="success")