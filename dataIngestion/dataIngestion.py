from extensions import mongo_client
from square.client import Client
from bson.objectid import ObjectId
from .config import *
from datetime import datetime


NUM_ORDER_GROUPS = 10


# retrieveSquareOrdersData
# inputs: none
# output: a json dataset of the data from the square orders API
def retrieve_square_orders_data(user_id):
    # get database access to get the square access token
    keystore_collection = mongo_client.db.KeyStore
    key = keystore_collection.find_one({'_id': ObjectId(user_id)})
    user_access_token = key['square_access_token']

    # create square sdk client
    client = Client(
        square_version='2021-10-20',
        access_token=user_access_token,
        environment='production'
    )

    order_count_collection = mongo_client.db.OrderCounts

    cursor = None
    cursor_count = NUM_ORDER_GROUPS
    # hashmap for storing order dates and counts
    order_counts = {}
    # boolean for checking if older order dates have been found
    older_dates_found = False

    # finds the most recent date in the database
    try:
        most_recent_date = (order_count_collection.find({}, {'datetime': 1}).sort([('datetime', -1)]).limit(1))[0]['datetime']
    except:
        most_recent_date = None

    # # For testing MOST_RECENT_DATE and skips first week
    # result = client.orders.search_orders(
    #     body={
    #         'location_ids': [
    #             LOCATION_ID
    #         ],
    #         'cursor': cursor
    #     }
    # )
    #
    # cursor = result.body['cursor']

    while cursor_count != 0:
        # made call to square orders API
        result = client.orders.search_orders(
            body={
                'location_ids': [
                    LOCATION_ID
                ],
                'cursor': cursor
            }
        )
        if result.is_success():
            # iterate through each order object
            for order in result.body['orders']:
                # get the date of the order as a datetime object
                try:
                    order_datetime = datetime.strptime(order['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                except:
                    order_datetime = datetime.strptime(order['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')

                # Setting H, M, S, and MS to 0 because we only want date and MongoDB doesn't accept date
                order_datetime = order_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

                # Checking if date is already in db to reduce redundancy
                if most_recent_date is not None and most_recent_date >= order_datetime:
                    older_dates_found = True
                    break

                # if the date already exists in the dictionary then increment its count
                if order_datetime in order_counts:
                    order_counts[order_datetime] = order_counts[order_datetime] + 1
                # if the date does not yet exist in the dictionary then create it and set its count to 1
                else:
                    order_counts[order_datetime] = 1

            # if other older order dates are found then stop adding redundant orders to db
            if older_dates_found:
                break

            # update the cursor for the next group of orders
            try:
                cursor = result.body['cursor']
            except:
                break
            
        else:
            return result.is_error()

        cursor_count = cursor_count - 1

    for key, value in order_counts.items():
        order_count_collection.insert_one({
            'datetime': key,
            'order_count': value,
        })

    return result.body
