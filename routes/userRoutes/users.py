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

    # check if form attributes are present
    if 'id' not in request.form:
        return Response("{'Error': 'Bad Request: Missing id field'}", status=400, mimetype='application/json')
    elif 'email' not in request.form:
        return Response("{'Error': 'Bad Request: Missing email field'}", status=400, mimetype='application/json')
    elif 'name' not in request.form:
        return Response("{'Error': 'Bad Request: Missing name field'}", status=400, mimetype='application/json')

    id = request.form.get('id')
    email = request.form.get('email')
    name = request.form.get('name')

    # check if a user with this ID already exists
    if user_collection.count_documents({ 'id': id }, limit = 1):
        return Response("{'Error': 'User already exists'}", status=403, mimetype='application/json')
    else:
        user_collection.insert_one({'id': id, 'email': email, 'name': name, 'forecasts': []})
        return jsonify(message="success")


# Get a user with the given ID
@userRoutes.route('/user/<user_id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def _get_user(user_id):
    user_collection = mongo_client.db.Users
    # determine whether the user exists
    if user_collection.count_documents({ 'id': user_id }, limit = 1):
        user = user_collection.find_one({'id': user_id})
        return json.loads(json_util.dumps(user))
    else:
        return Response("{'Error': 'No such user with the given ID'}", status=404, mimetype='application/json')


# Update the email address of a user with the given ID
@userRoutes.route('/user/<user_id>', methods=['PUT'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def _edit_user(user_id):
    user_collection = mongo_client.db.Users

    new_email = request.form.get('email')
    new_name = request.form.get('name')

    # determine whether the user exists
    if user_collection.count_documents({ 'id': user_id }, limit = 1):
        user = user_collection.replace_one({'id': user_id}, {'id': user_id, 'email': new_email, 'name': new_name, 'forecasts': []})
        return json.loads(json_util.dumps(user.raw_result))
    else:
        return Response("{'Error': 'No such user with the given ID'}", status=404, mimetype='application/json')


# Delete the user with the given ID
@userRoutes.route('/user/<user_id>', methods=['DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def _delete_user(user_id):
    user_collection = mongo_client.db.Users

    if user_collection.count_documents({ 'id': user_id }, limit = 1):
        user = user_collection.delete_one({'id': user_id})
        return json.loads(json_util.dumps(user.raw_result))
    else:
        return Response("{'Error': 'No such user with the given ID'}", status=404, mimetype='application/json')


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
    # create_model(user_id)

    return {
        'message': 'temporarily disabled'
    }


# get_prediction
# get a prediction from the ml model
@userRoutes.route('/user/<user_id>/prediction/<date>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def get_prediction(user_id, date):
    # temporary check to make sure it is crabtrees user ID accessing his data
    if user_id != os.environ.get('CRABTREE_USER_ID'):
        return Response("{'Error': 'Forbidden (Non-Crabtree user)'}", status=403, mimetype='application/json')
    # check if the date is present
    if 'date' == None:
        return Response("{'Error': 'Bad Request: Missing date field'}", status=400, mimetype='application/json')

    # make a prediction with the ml model
    prediction = make_prediction(date, 'customer_volume_model')

    return {
        'prediction': prediction[0]
    }
