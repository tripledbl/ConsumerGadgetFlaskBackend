import os
from routes.authorization import requires_auth, AuthError, handle_auth_error
from flask_cors import cross_origin
from extensions import *
from MLModels import *

modelRoutes = Blueprint('modelRoutes', __name__)

# Error handler
modelRoutes.register_error_handler(AuthError, handle_auth_error)

# Assign api_audience
model_api_audience = os.environ.get('MODEL_API_AUDIENCE')

# createModel
# create a machine learning model using predetermined data and inputs
@modelRoutes.route('/createModel/<string:user_id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=model_api_audience)
def createModel(user_id):
    # temporary check to make sure it is crabtrees user ID accessing his data
    if user_id != os.environ.get('CRABTREE_USER_ID'):
        return {
            'message': 'this user ID cannot create models'
        }

    # create a machine learning model
    create_model()


    return {
        'message': 'success'
    }
