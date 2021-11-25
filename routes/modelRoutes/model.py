from routes.authorization import requires_auth, AuthError, handle_auth_error
from flask_cors import cross_origin
from extensions import *
from dataIngestion import retrieve_square_orders_data

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

    # get the orders data from the users square account
    res = retrieve_square_orders_data(user_id)

    return res
