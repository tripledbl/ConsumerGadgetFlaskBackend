import os
from routes.authorization import requires_auth, AuthError, handle_auth_error
from flask_cors import cross_origin
from extensions import *
from dataIngestion import orders_to_dateframe, add_day_of_week, retrieve_square_orders_data

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

    # get the orders data from the users square account
    orders_df = orders_to_dateframe()
    orders_df = add_day_of_week(orders_df)

    print(orders_df)

    return {
        'message': 'success'
    }
