from datetime import datetime, timedelta
from uuid import uuid4
import base64

import jwt
from flask import current_app

from app.models.refresh_token import RefreshToken
from app import db


def encode_jwt(secret, algorithm, duration, additional_claims=None):
    """
    encodes (utf-8) JWT

    :param secret: key used to sign the token.
    :param algorithm: algorithm to sign the token.
    :param duration: time until the token expires. Parameter is a timedelta
    :param additional_claims: any other claims to provide to the token.
    """
    jti = str(uuid4())
    now = datetime.utcnow()

    claims = {"iat": now, "exp": now + duration, "jti": jti}

    if additional_claims is not None:
        claims.update(additional_claims)

    return jwt.encode(claims, secret, algorithm=algorithm).decode("utf-8")


def decode_jwt(token, secret, algorithm, options=None):
    """
    Decodes JWT and validates if its valid

    :param token: JWT to decode
    :param secret: secret used to verify signature
    :param algorithm: algorithm used to sign JWT
    :returns jwt claims
    """
    if options is not None:
        return jwt.decode(
            token, secret, algorithms=[algorithm], options=options)

    return jwt.decode(token, secret, algorithms=[algorithm])


def create_access_token(user_id, user_claims=None):
    """
    Creates access token

    :param user_id: id of user who owns this token. can be any identifier like
                    a username, email, uuid, etc.
    :param user_claims: additional claims to encode in jwt.
    :returns encoded jwt string
    """

    jwt_claims = {"user_id": user_id}

    if user_claims is not None:
        jwt_claims.update(user_claims)

    return encode_jwt(current_app.config["JWT_SECRET"],
                      current_app.config["JWT_ALGORITHM"],
                      current_app.config["ACCESS_TOKEN_DURATION"], jwt_claims)


def create_refresh_token(user_id, jti):
    """
    Creates refresh token, adds to database session, commit should be handled 
    outside function.

    :param user_id: user id
    :param jti: access token jti
    :returns refresh token string
    """

    token = str(uuid4())

    refresh_token = RefreshToken(token, user_id=user_id, access_token_jti=jti)

    db.session.add(refresh_token)

    return refresh_token


def set_access_token_cookie(response, access_token):
    """
    Sets access token in cookie

    :param response: flask response object
    :param access_token: access token
    """

    now = datetime.utcnow()

    b64encoded_access_token = base64.b64encode(bytes(access_token, "utf-8"))

    response.set_cookie(
        current_app.config["ACCESS_TOKEN_COOKIE_NAME"],
        b64encoded_access_token,
        secure=current_app.config["SECURE_ACCESS_TOKEN_COOKIE"],
        expires=now + current_app.config["ACCESS_TOKEN_EXPIRATION"],
        httponly=True)


def set_refresh_token_cookie(response, refresh_token):
    """
    Sets refresh token in cookie

    :param response: flask response object
    :param refresh_token: refresh token
    """

    response.set_cookie(
        current_app.config["REFRESH_TOKEN_COOKIE_NAME"],
        refresh_token,
        secure=current_app.config["SECURE_REFRESH_TOKEN_COOKIE"],
        expires=now + current_app.config["REFRESH_TOKEN_EXPIRATION"],
        httponly=True)


def get_access_token_from_cookie():
    """
    Returns access token from the cookie
    """

    b64encoded_access_token = request.cookies[
        current_app.config["ACCESS_TOKEN_COOKIE_NAME"]]

    access_token = base64.b64decode(b64encoded_access_token).decode("utf-8")

    return access_token


def get_refresh_token_from_cookie():
    """
    Returns refresh token from the cookie
    """

    refresh_token = request.cookies[current_app.
                                    config["REFRESH_TOKEN_COOKIE_NAME"]]

    return refresh_token


# TODO: refactor, divide decorator
def authentication_required(f):
    """
    Checks access token validity
    """

    @wraps
    def f_wrapper(*args, **kwargs):

        try:
            access_token = get_access_token_from_cookie()
        except KeyError:
            return jsonify({"message": "invalid token"}), 401

        try:
            _app_ctx_stack.top.jwt_claims = decode_jwt(
                access_token, current_app.config["JWT_SECRET"],
                current_app.config["JWT_ALGORITHM"])
        except jwt.exceptions.ExpiredSignatureError:

            try:
                refresh_token = get_refresh_token_from_cookie()
            except KeyError:
                return jsonify({"message": "invalid token"}), 401

            refresh_token = RefreshToken.first(token=refresh_token)

            if refresh_token is not None and refresh_token.is_valid():
                jwt_claims = decode_jwt(
                    access_token,
                    current_app.config["JWT_SECRET"],
                    current_app.config["JWT_ALGORITHM"],
                    options={"verify_exp": False})

                if not refresh_token.is_jti_valid(jwt_claims.jti):
                    # check if access token is blacklisted if it isn't
                    # jwt secret has been compromised

                    refresh_token.revoke_user_tokens(refresh_token)
                    return jsonify({"message": "invalid token"}), 401

                new_access_token = create_access_token(jwt_claims.user_id,
                                                       jwt_claims)

                _app_ctx_stack.top.new_access_token = new_access_token
                return f(*args, **kwargs)

            return jsonify({"message": "invalid token"}), 401
        except jwt.exceptions.InvalidTokenError:
            return jsonify({"message": "invalid token"}), 401

        return f(*args, **kwargs)

    return f_wrapper


def access_token_required(f):
    """
    Decorator for routes that require the access token
    """

    @wraps(f)
    def f_wrapper(*args, **kwargs):

        try:
            access_token = get_access_token_from_cookie()
        except KeyError:
            return jsonify({"message": "access token not in cookies"}), 401

        try:
            _app_ctx_stack.top.jwt_claims = decode_jwt(
                access_token, current_app.config["JWT_SECRET"],
                current_app.config["JWT_ALGORITHM"])

        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({"message": "expired access token"}), 401
        except jwt.exceptions.PyJWTError:
            return jsonify({"message": "invalid access token"}), 401

        return f(*args, **kwargs)

    return f_wrapper
