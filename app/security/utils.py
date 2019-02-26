import functools

import jwt
import flask

from app.security import token_auth

ADMINISTRATOR = "administrator"
MODERATOR = "moderator"
BASIC = "basic"


#TODO: return user model instead of just user_id.
#TODO: use username for jwt instead of user_id.
def get_current_user():
    """Gets current user from jwt token cookie.

    Returns:
        string: current user's user_id.
        None: if there's an error.
    """

    try:
        access_token = token_auth.get_access_token_from_cookie()
    except KeyError:
        return None

    try:
        jwt_claims = token_auth.decode_jwt(
            access_token, flask.current_app.config["JWT_SECRET"],
            flask.current_app.config["JWT_ALGORITHM"])

    except jwt.exceptions.ExpiredSignatureError:

        jwt_claims = token_auth.decode_jwt(
            access_token,
            flask.current_app.config["JWT_SECRET"],
            flask.current_app.config["JWT_ALGORITHM"],
            options={"verify_exp": False})

    except jwt.exceptions.InvalidTokenError:
        return None

    try:
        return jwt_claims["user_id"]
    except KeyError:
        return None


def get_claims():
    """Gets the jwt token claims from cookie.

    Returns:
        Dict: jwt claims.
        None: if there's an error.
    """

    try:
        access_token = token_auth.get_access_token_from_cookie()
    except KeyError:
        return None

    try:
        jwt_claims = token_auth.decode_jwt(
            access_token, flask.current_app.config["JWT_SECRET"],
            flask.current_app.config["JWT_ALGORITHM"])

    except jwt.exceptions.ExpiredSignatureError:

        jwt_claims = token_auth.decode_jwt(
            access_token,
            flask.current_app.config["JWT_SECRET"],
            flask.current_app.config["JWT_ALGORITHM"],
            options={"verify_exp": False})

    except jwt.exceptions.InvalidTokenError:
        return None

    try:
        return jwt_claims
    except KeyError:
        return None


def user_role(roles):
    """Allowed user roles decorator.

    Checks if the user has the role needed to access this route

    Args:
        roles (list) (required): list of user roles needed.

    Returns:
        obj: flask response, a message if the user is not authorized with 
            error code 403.
    """

    def user_role_decorator(f):

        @functools.wraps(f)
        def f_wrapper(*args, **kwargs):

            claims = get_claims()

            if claims is None or claims["role"] not in roles:
                return flask.jsonify({"message": "user not authorized"}), 403

            return f(*args, **kwargs)

        return f_wrapper

    return user_role_decorator
