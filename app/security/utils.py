from functools import wraps

import jwt
from flask import current_app, jsonify

from .token_auth.utils import decode_jwt, get_access_token_from_cookie

ADMINISTRATOR = "administrator"
MODERATOR = "moderator"
BASIC = "basic"


def get_current_user():
    """
    Returns the current user
    """

    try:
        access_token = get_access_token_from_cookie()
    except KeyError:
        return None

    try:
        jwt_claims = decode_jwt(access_token, current_app.config["JWT_SECRET"],
                                current_app.config["JWT_ALGORITHM"])

    except jwt.exceptions.ExpiredSignatureError:

        jwt_claims = decode_jwt(
            access_token,
            current_app.config["JWT_SECRET"],
            current_app.config["JWT_ALGORITHM"],
            options={"verify_exp": False})

    except jwt.exceptions.InvalidTokenError:
        return None

    try:
        return jwt_claims["user_id"]
    except KeyError:
        return None


def get_claims():
    """
    Returns the claims
    """

    try:
        access_token = get_access_token_from_cookie()
    except KeyError:
        return None

    try:
        jwt_claims = decode_jwt(access_token, current_app.config["JWT_SECRET"],
                                current_app.config["JWT_ALGORITHM"])

    except jwt.exceptions.ExpiredSignatureError:

        jwt_claims = decode_jwt(
            access_token,
            current_app.config["JWT_SECRET"],
            current_app.config["JWT_ALGORITHM"],
            options={"verify_exp": False})

    except jwt.exceptions.InvalidTokenError:
        return None

    try:
        return jwt_claims
    except KeyError:
        return None


def user_role(roles):
    """
    Checks if the user has the role needed to access this route

    :params roles: user roles needed
    """

    def user_role_decorator(f):

        @wraps(f)
        def f_wrapper(*args, **kwargs):

            claims = get_claims()

            if claims is None or claims["role"] not in roles:
                return jsonify({"message": "user not authorized"}), 403

            return f(*args, **kwargs)

        return f_wrapper

    return user_role_decorator
