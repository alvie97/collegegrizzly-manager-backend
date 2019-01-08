from datetime import datetime, timedelta
from uuid import uuid4
import base64

import jwt
from flask import current_app


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
    """
    if options is not None:
        return jwt.decode(
            token, secret, algorithms=[algorithm], options=options)

    return jwt.decode(token, secret, algorithms=[algorithm])


def create_auth_token(user_id, user_claims=None):
    """
    Creates auth token

    :param user_id: id of user who owns this token. can be any identifier like
                    a username, email, uuid, etc.
    :param user_claims: additional claims to encode in jwt.
    """

    jwt_claims = {"user_id": user_id}

    if user_claims is not None:
        jwt_claims.update(user_claims)

    return encode_jwt(current_app.config["JWT_SECRET"],
                      current_app.config["JWT_ALGORITHM"],
                      current_app.config["AUTH_TOKEN_DURATION"], jwt_claims)


def set_auth_token_cookie(response, user_id, token_claims=None):
    """
    Sets auth token in cookie

    :param response: flask response object
    :param user_id: user id to attatch to JWT
    :param token_claims: auth token claims
    """

    auth_token = create_auth_token(user_id, token_claims)

    now = datetime.utcnow()

    b64encoded_auth_token = base64.b64encode(bytes(auth_token, "utf-8"))

    response.set_cookie(
        current_app.config["AUTH_TOKEN_COOKIE_NAME"],
        b64encoded_auth_token,
        secure=current_app.config["SECURE_AUTH_TOKEN_COOKIE"],
        expires=now + current_app.config["AUTH_TOKEN_EXPIRATION"],
        httponly=True)


def get_auth_token_from_cookie():
    """
    Returns auth token from the cookie
    """

    b64encoded_auth_token = request.cookies[current_app.
                                            config["AUTH_TOKEN_COOKIE_NAME"]]

    auth_token = base64.b64decode(b64encoded_auth_token).decode("utf-8")

    return auth_token


def auth_token_required(f):
    """
    Decorator for routes that require the auth token
    """

    @wraps(f)
    def f_wrapper(*args, **kwargs):

        try:
            auth_token = get_auth_token_from_cookie()
        except KeyError:
            return jsonify({"message": "auth token not in cookies"}), 401

        try:
            _app_ctx_stack.top.jwt_claims = decode_jwt(
                access_token, current_app.config["JWT_SECRET"],
                current_app.config["JWT_ALGORITHM"])

        except ExpiredSignatureError:
            return jsonify({"message": "expired auth token"}), 401
        except PyJWTError:
            return jsonify({"message": "invalid auth token"}), 401

        return f(*args, **kwargs)

    return f_wrapper