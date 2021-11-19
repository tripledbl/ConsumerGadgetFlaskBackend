import app
from extensions import *
import json
from six.moves.urllib.request import urlopen
from functools import wraps
from flask import Flask, request, jsonify, _request_ctx_stack
from flask_cors import cross_origin
from jose import jwt

userRoutes = Blueprint('userRoutes', __name__)

AUTH0_DOMAIN = '127.0.0.1:5000'
API_AUDIENCE = 'http://127.0.0.1:5000/user'
ALGORITHMS = ["RS256"]


# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@userRoutes.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def get_token_auth_header():
    # Obtains the Access Token from the Authorization Header
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                             "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must start with"
                             " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be"
                             " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    # Determines if the Access Token is valid
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("http://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://" + AUTH0_DOMAIN + "/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                 "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                 "description":
                                     "incorrect claims,"
                                     "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                 "description":
                                     "Unable to parse authentication"
                                     " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)

    return decorated


# @userRoutes.route('/user/<user_id>', methods=['GET'])
# @cross_origin(headers=["Content-Type", "Authorization"])
# @requires_auth
# def _get_user(user_id):
#     user_collection = mongo_client.db.Users
#     user = user_collection.find_one({'_id': ObjectId(user_id)})
#     # have to use json_util because the ObjectId in the user object cannot be directly turned to json
#     return json.loads(json_util.dumps(user))


@userRoutes.route('/user', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def _create_user():
    user_collection = mongo_client.db.Users
    email = request.form.get('email')
    # subject to change, must make this id the same as the ID passed by Auth0 from the frontend
    id = request.form.get('id')
    user_collection.insert_one({'_id': ObjectId(id), 'email': email, 'models': []})
    return jsonify(message="success")