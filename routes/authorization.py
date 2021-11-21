from functools import wraps

from flask import _request_ctx_stack
from jose import jwt
from six.moves.urllib.request import urlopen

from extensions import *

AUTH0_DOMAIN = 'predictant.us.auth0.com'
ALGORITHMS = ["RS256"]


# Error Class
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Error handler
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


def requires_auth(*, audience):
    api_audience = audience

    def inner_requires_auth(f):
        # Determines if the Access Token is valid
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header()
            jsonurl = urlopen("http://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
            jwks = json.loads(jsonurl.read())
            try:
                unverified_header = jwt.get_unverified_header(token)
            except:
                raise AuthError({"code": "invalid_header",
                                 "description": "Invalid Token"}, 401)
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
                        audience=api_audience,
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

    return inner_requires_auth
