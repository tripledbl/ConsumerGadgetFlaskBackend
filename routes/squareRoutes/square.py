from flask import Blueprint, request, current_app
import datetime
from square.client import Client
from .config import *

squareRoutes = Blueprint('squareRoutes', __name__)

# get Square OAuth token
@squareRoutes.route('/squareOAuth', methods=['GET'])
def getSquareOAuth():
    res = request.values
    code = res.get('code')
    # get the token from the square OAuth endpoint
    api_res = obtainToken(code)
    print(api_res)
    return api_res

# obtainToken
# inputs:
#   - token: a properly formatted OAuth token that can be used to call the Square's ObtainToken endpoint
# output: the token returned by Square's ObtainToken endpoint
def obtainToken(token):

    # create square sdk client
    client = Client(
        access_token=token,
        environment='sandbox'
    )

    # set up inputs to obtainToken endpoint
    client_id = current_app.config['SQUARE_CLIENT_ID']
    client_secret = current_app.config['SQUARE_CLIENT_SECRET']
    grant_type = 'authorization_code'

    result = client.o_auth.obtain_token(
        body = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": token,
            "grant_type": grant_type
        }
    )

    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)

    # retrieve the access token
    token = result.body['access_token']

    # test the orders API
    orders = retrieveSquareOrdersData(token)

    return orders

# retrieveSquareOrdersData
# inputs:
#   - access_token: a token that allows the application access to square data
# output: a json dataset of the data from the square orders API
def retrieveSquareOrdersData(access_token):

    # create square sdk client
    client = Client(
        access_token=access_token,
        environment='sandbox'
    )

    # made call to square orders API
    result = client.orders.search_orders(
        body = {
            "location_ids": [
                LOCATION_ID
            ],
            "query": {
                "filter": {
                    "state_filter": {
                        "states": [
                            "COMPLETED"
                        ]
                    },
                    "date_time_filter": {
                        "closed_at": {
                            "start_at": "2018-03-03",
                            "end_at": datetime.datetime.now()
                        }
                    }
                },
                "sort": {
                    "sort_field": "CLOSED_AT",
                    "sort_order": "DESC"
                }
            }
        }
    )

    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)

    return result.body

# createOrder
# inputs: an access token that allows access to square APIs
# outputs: creates a new order in the square database
def createOrder(access_token):

    # create square sdk client
    client = Client(
        access_token=access_token,
        environment='sandbox'
    )

    result = client.orders.create_order(
    body = {
        "order": {
            "location_id": LOCATION_ID,
            "reference_id": "my-order-001",
            "line_items": [
                {
                    "name": "New York Strip Steak",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1599,
                        "currency": "USD"
                    }
                },
            ],
        },
        "idempotency_key": "8193148c-9586-11e6-99f9-28cfe92138cf"
    }
    )

    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)

    return result.body
