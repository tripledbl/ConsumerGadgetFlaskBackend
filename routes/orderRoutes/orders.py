from dataIngestion import retrieve_square_orders_data
from routes.authorization import requires_auth, AuthError, handle_auth_error
from flask_cors import cross_origin
from extensions import *
from datetime import datetime, timedelta

orderRoutes = Blueprint('orderRoutes', __name__)

# Error handler
orderRoutes.register_error_handler(AuthError, handle_auth_error)

# Assign api_audience
orders_api_audience = os.environ.get('ORDERS_API_AUDIENCE')


# retrieve_square_orders_data
# inputs: Square account user id
# output: a json dataset of the data from the square orders API
@orderRoutes.route('/orders', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=orders_api_audience)
def store_order_groups():
    # check if from_date in form
    if 'user_id' not in request.form:
        return Response("{'Error': 'Bad Request: Missing user_id'}", status=400, mimetype='application/json')
    else:
        user_id = request.form.get('user_id')
    # get the orders data from the users square account
    res = retrieve_square_orders_data(user_id)

    return res


# Get orders from a passed in date range from db
@orderRoutes.route('/orders/<string:from_date>/<string:to_date>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=orders_api_audience)
def get_order_groups(from_date, to_date):
    # check if from_date in form
    if 'from_date' == None:
        return Response("{'Error': 'Bad Request: Missing from_date'}", status=400, mimetype='application/json')

    # check if to_date in form
    if 'to_date' == None:
        return Response("{'Error': 'Bad Request: Missing to_date'}", status=400, mimetype='application/json')

    order_counts_collection = mongo_client.db.OrderCounts
    # Converting strings to datetime objets
    from_date = datetime.strptime(from_date + "T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
    to_date = datetime.strptime(to_date + "T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
    order_groups = {}
    # Grabbing orderGroups using from_date until it reaches the day before the to_date
    for order in order_counts_collection.find({"datetime": {"$gte": from_date, "$lte": to_date}}):
        order_groups[order['datetime'].strftime('%Y-%m-%d')] = order['order_count']

    return order_groups
