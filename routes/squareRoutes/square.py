from flask import Blueprint, request, current_app
import requests
import json
from .paths import SQUARE_OBTAIN_TOKEN

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
    # set up inputs to obtainToken endpoint
    client_id = current_app.config['SQUARE_CLIENT_ID']
    client_secret = current_app.config['SQUARE_CLIENT_SECRET']
    grant_type = 'authorization_code'

    # make API call
    json_res = requests.post(SQUARE_OBTAIN_TOKEN,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": token,
            "grant_type": grant_type
        }
    )

    res = json.loads(json_res.text)
    access_token = res['access_token']

    return access_token
