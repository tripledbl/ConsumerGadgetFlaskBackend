import json
from flask import Blueprint
from flask import jsonify
from flask import request
from bson import json_util
from bson.objectid import ObjectId
from extensions import mongo_client

userRoutes = Blueprint('userRoutes', __name__)

# Create a new user
@userRoutes.route('/user', methods=['POST'])
def createUser():
    user_collection = mongo_client.db.Users
    email = request.form.get('email')
    # subject to change, must make this id the same as the ID passed by Auth0 from the frontend
    id = request.form.get('id')
    user_collection.insert_one({'_id': ObjectId(id), 'email': email, 'models': []})
    return jsonify(message="success")

# Get a user with the given ID
@userRoutes.route('/user/<string:userId>', methods=['GET'])
def getUser(userId):
    user_collection = mongo_client.db.Users
    user = user_collection.find_one({'_id': ObjectId(userId)})
    # have to use json_util because the ObjectId in the user object cannot be directly turned to json
    return json.loads(json_util.dumps(user))

# Update the email address of a user with the given ID
@userRoutes.route('/user/<string:userId>', methods=['PUT'])
def editUser(userId):
    user_collection = mongo_client.db.Users
    newEmail = request.form.get('email')
    # use 'id' instead of '_id' temporarily
    user = user_collection.replace_one({'_id': ObjectId(userId)}, {'email': newEmail, 'models': []})
    return json.loads(json_util.dumps(user.raw_result))

# Delete the user with the given ID
@userRoutes.route('/user/<string:userId>', methods=['DELETE'])
def deleteUser(userId):
    user_collection = mongo_client.db.Users
    user = user_collection.delete_one({'_id': ObjectId(userId)})
    return json.loads(json_util.dumps(user.raw_result))