import json
from flask import Blueprint, jsonify, request
from bson import json_util
from bson.objectid import ObjectId
from extensions import mongo_client

userRoutes = Blueprint('userRoutes', __name__)


# Create a new user
@userRoutes.route('/user', methods=['POST'])
def _create_user():
    user_collection = mongo_client.db.Users
    email = request.form.get('email')
    # subject to change, must make this id the same as the ID passed by Auth0 from the frontend
    id = request.form.get('id')
    user_collection.insert_one({'_id': ObjectId(id), 'email': email, 'models': []})
    return jsonify(message="success")


# Get a user with the given ID
@userRoutes.route('/user/<user_id>', methods=['GET'])
def _get_user(user_id):
    user_collection = mongo_client.db.Users
    user = user_collection.find_one({'_id': ObjectId(user_id)})
    # have to use json_util because the ObjectId in the user object cannot be directly turned to json
    return json.loads(json_util.dumps(user))


# Update the email address of a user with the given ID
@userRoutes.route('/user/<user_id>', methods=['PUT'])
def _edit_user(user_id):
    user_collection = mongo_client.db.Users
    new_email = request.form.get('email')
    # use 'id' instead of '_id' temporarily
    user = user_collection.replace_one({'_id': ObjectId(user_id)}, {'email': new_email, 'models': []})
    return json.loads(json_util.dumps(user.raw_result))


# Delete the user with the given ID
@userRoutes.route('/user/<user_id>', methods=['DELETE'])
def _delete_user(user_id):
    user_collection = mongo_client.db.Users
    user = user_collection.delete_one({'_id': ObjectId(user_id)})
    return json.loads(json_util.dumps(user.raw_result))
