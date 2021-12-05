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
def create_model(user_id):
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
@userRoutes.route('/user/<user_id>/prediction/<from_date>/<to_date>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=user_api_audience)
def get_prediction(user_id, from_date, to_date):
    # temporary check to make sure it is crabtrees user ID accessing his data
    if user_id != os.environ.get('CRABTREE_USER_ID'):
        return Response("{'Error': 'Forbidden (Non-Crabtree user)'}", status=403, mimetype='application/json')
    # check if the date is present
    if 'from_date' == None:
        return Response("{'Error': 'Bad Request: Missing from_date field'}", status=400, mimetype='application/json')
    if 'to_date' == None:
        return Response("{'Error': 'Bad Request: Missing to_date field'}", status=400, mimetype='application/json')

    # cast the date string to a date
    from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

    if from_date > to_date:
        return Response("{'Error': 'Bad Request: from_date is greater than to_date'}", status=400, mimetype='application/json')

    # cast to datetime so the column conversions work in make_prediction()
    time = datetime.min.time()
    from_date = datetime.combine(from_date, time)
    to_date = datetime.combine(to_date, time)

    # create an array with all of the date strings
    dates = []
    while from_date <= to_date:
        dates.append(from_date.strftime('%Y-%m-%d'))
        from_date = from_date + timedelta(days=1)

    predictions = make_prediction(dates, 'customer_volume_model')

    # return dictionary
    res = {}
    # keep track of array index
    index = 0
    # add each date and prediction to an object
    for prediction in predictions:
        res[dates[index]] = prediction
        index = index + 1

    return res
