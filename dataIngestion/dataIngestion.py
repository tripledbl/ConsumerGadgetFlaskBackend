from extensions import mongo_client
from square.client import Client
from bson.objectid import ObjectId
from .config import *


# retrieveSquareOrdersData
# inputs: none
# output: a json dataset of the data from the square orders API
def retrieveSquareOrdersData(user_id):

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

    api_locations = client.locations
    res = api_locations.list_locations()
    print(res)

    # made call to square orders API
    result = client.orders.search_orders(
        body = {
            'location_ids': [
                LOCATION_ID
            ]
        }
    )

    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)

    return result.body