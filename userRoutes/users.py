from flask import Blueprint
from flask import jsonify
from flask import request
from database import mongo_client

userRoutes = Blueprint('userRoutes', __name__)

@userRoutes.route('/user', methods=['POST'])
def user():
    user_collection = mongo_client.db.Users
    email = request.args.get('email')
    id = request.args.get('id')
    user_collection.insert_one({'email': email, 'id': id})
    return jsonify(message="success")