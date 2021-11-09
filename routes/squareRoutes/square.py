from flask import Blueprint, request, current_app
import requests
from .paths import SQUARE_OBTAIN_TOKEN

squareRoutes = Blueprint('squareRoutes', __name__)

# get Square OAuth token
@squareRoutes.route('/squareOAuth', methods=['GET'])
def getSquareOAuth():
    res = request.values
    code = res.get('code')
    apiRes = obtainToken(code)
    print(apiRes.text)
    return apiRes.json()

# obtainToken
# inputs:
#       token: a properly formatted OAuth token that can be used to call the Square's ObtainToken endpoint
# output: the token returned by Square's ObtainToken endpoint
def obtainToken(token):
    # set up inputs to obtainToken endpoint
    client_id = current_app.config['SQUARE_CLIENT_ID']
    client_secret = current_app.config['SQUARE_CLIENT_SECRET']
    grant_type = 'authorization_code'
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": token,
        "grant_type": grant_type
    }

    # make API call
    res = requests.post(SQUARE_OBTAIN_TOKEN, data=data)

    return res
