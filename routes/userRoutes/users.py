from routes.authorization import requires_auth, AuthError, handle_auth_error
from flask_cors import cross_origin
from extensions import *
from MLModels import *

userRoutes = Blueprint('userRoutes', __name__)

# Error handler
userRoutes.register_error_handler(AuthError, handle_auth_error)

# Assign api_audience
user_api_audience = os.environ.get('USER_API_AUDIENCE')


# Create a new user
@userRoutes.route('/user', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def _create_user():
    user_collection = mongo_client.db.Users
    email = request.form.get('email')
    # subject to change, must make this id the same as the ID passed by Auth0 from the frontend
    id = request.form.get('id')
    user_collection.insert_one({'_id': ObjectId(id), 'email': email, 'models': []})
    return jsonify(message="success")


# Get a user with the given ID
@userRoutes.route('/user/<user_id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def _get_user(user_id):
    user_collection = mongo_client.db.Users
    user = user_collection.find_one({'_id': ObjectId(user_id)})
    # have to use json_util because the ObjectId in the user object cannot be directly turned to json
    return json.loads(json_util.dumps(user))


# Update the email address of a user with the given ID
@userRoutes.route('/user/<user_id>', methods=['PUT'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def _edit_user(user_id):
    user_collection = mongo_client.db.Users
    new_email = request.form.get('email')
    # use 'id' instead of '_id' temporarily
    user = user_collection.replace_one({'_id': ObjectId(user_id)}, {'email': new_email, 'models': []})
    return json.loads(json_util.dumps(user.raw_result))


# Delete the user with the given ID
@userRoutes.route('/user/<user_id>', methods=['DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def _delete_user(user_id):
    user_collection = mongo_client.db.Users
    user = user_collection.delete_one({'_id': ObjectId(user_id)})
    return json.loads(json_util.dumps(user.raw_result))

# createModel
# create a machine learning model using predetermined data and inputs
@userRoutes.route('/user/<user_id>/model', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def createModel(user_id):
    # temporary check to make sure it is crabtrees user ID accessing his data
    if user_id != os.environ.get('CRABTREE_USER_ID'):
        return {
            'message': 'this user ID cannot create models'
        }

    # create a machine learning model
    create_model(user_id)


    return {
        'message': 'success'
    }

# get_prediction
# get a prediction from the ml model
@userRoutes.route('/user/<user_id>/prediction', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def get_prediction(user_id):
    # temporary check to make sure it is crabtrees user ID accessing his data
    if user_id != os.environ.get('CRABTREE_USER_ID'):
        return {
            'message': 'this user ID cannot get predictions'
        }
    # check if the date is present
    if 'date' not in request.form:
        return Response("{'Error': 'Bad Request: Missing date field'}", status=400, mimetype='application/json')
    else:
        date = request.form.get('date')

    # make a prediction with the ml model
    prediction = make_prediction(date, 'customer_volume_model')

    return {
        'prediction': prediction[0]
    }