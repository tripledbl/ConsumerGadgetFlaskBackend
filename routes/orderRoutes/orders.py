from routes.authorization import requires_auth, AuthError, handle_auth_error
from flask_cors import cross_origin
from extensions import *
from datetime import datetime, timedelta

orderRoutes = Blueprint('orderRoutes', __name__)

# Error handler
orderRoutes.register_error_handler(AuthError, handle_auth_error)

# Assign api_audience
orders_api_audience = os.environ.get('ORDER_API_AUDIENCE')


# Get orders from a passed in date range from db
@orderRoutes.route('/orders/<string:from_date>/<string:to_date>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(audience=orders_api_audience)
def get_historical_weather(from_date, to_date):
    order_counts_collection = mongo_client.db.OrderCounts
    # Converting strings to datetime objets
    from_date = datetime.strptime(from_date + "T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
    to_date = datetime.strptime(to_date + "T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
    order_groups = {}
    # Grabbing orderGroups using from_date until it reaches the day before the to_date
    while from_date < to_date:
        for order in order_counts_collection.find({"datetime": {"$gte": from_date, "$lt": to_date}}):
            order_groups[order['datetime'].strftime('%Y-%m-%d')] = order['order_count']
        from_date = from_date + timedelta(days=1)

    return order_groups
