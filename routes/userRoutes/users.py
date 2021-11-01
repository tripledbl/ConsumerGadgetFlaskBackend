import json
from flask import Blueprint
from flask import jsonify
from flask import request
from bson import json_util
from extensions import mongo_client

userRoutes = Blueprint('userRoutes', __name__)

# Create a new user
@userRoutes.route('/user', methods=['POST'])
def createUser():
    user_collection = mongo_client.db.Users
    email = request.form.get('email')
    # subject to change, must make this id the same as the ID passed by Auth0 from the frontend
    id = request.form.get('id')
    user_collection.insert_one({'id': id, 'email': email, 'models': []})
    return jsonify(message="success")

# Get a user with the given ID
@userRoutes.route('/user/<string:userId>', methods=['GET'])
def getUser(userId):
    user_collection = mongo_client.db.Users
    user = user_collection.find_one({'id': userId})
    # have to use json_util because the ObjectId in the user object cannot be directly turned to json
    return json.loads(json_util.dumps(user))