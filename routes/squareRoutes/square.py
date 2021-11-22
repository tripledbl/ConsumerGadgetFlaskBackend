from flask import Blueprint, current_app
from square.client import Client
from bson.objectid import ObjectId

squareRoutes = Blueprint('squareRoutes', __name__)

# TEMPORARILY DISABLED BECAUSE TOKEN ALREADY OBTAINED
# get Square OAuth token
# this endpoint is called by square APIs when the square account owner accepts the square integrations with our application
# @squareRoutes.route('/squareOAuth', methods=['GET'])
# def getSquareOAuth():
#     res = request.values
#     code = res.get('code')

#     # get the token from the square OAuth endpoint
#     api_res = obtainToken(code)

#     # create database client to store the keys
#     keystore_collection = mongo_client.db.KeyStore

#     # insert keys into database
#     access_token = api_res['access_token']
#     refresh_token = api_res['refresh_token']
#     keystore_collection.replace_one(
#         {
#             '_id': ObjectId(current_app.config['CRABTREE_USER_ID']),
#         },
#         {
#             'square_access_token': access_token,
#             'square_refresh_token': refresh_token
#         }
#     )

#     return api_res

# obtainToken
# inputs:
#   - token: a properly formatted OAuth token that can be used to call the Square's ObtainToken endpoint
# output: the token returned by Square's ObtainToken endpoint
def obtainToken(token):

    # create square sdk client
    client = Client(
        access_token=token,
        environment='production'
    )

    # set up inputs to obtainToken endpoint
    client_id = current_app.config['SQUARE_CLIENT_ID']
    client_secret = current_app.config['SQUARE_CLIENT_SECRET']
    grant_type = 'authorization_code'

    # get the tokens from the square authentication API
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

    return result.body
