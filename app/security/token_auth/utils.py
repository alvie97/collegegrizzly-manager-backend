from datetime import datetime, timedelta
from uuid import uuid4
from functools import wraps
import base64

import jwt
from flask import current_app, g, request, jsonify, make_response
from sqlalchemy import and_

from app.models.refresh_token import RefreshToken
from app import db
from app.security.csrf import clear_csrf_token_cookies


def encode_jwt(secret, algorithm, duration, additional_claims=None):
    """
    encodes (utf-8) JWT

    :param secret: key used to sign the token.
    :param algorithm: algorithm to sign the token.
    :param duration: time until the token expires. Parameter is a timedelta
    :param additional_claims: any other claims to provide to the token.
    """
    now = datetime.utcnow()

    claims = {"iat": now, "exp": now + duration}

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

    jti = str(uuid4())
    jwt_claims = {"user_id": user_id, "jti": jti}

    if user_claims is not None:
        user_claims.update(jwt_claims)
        jwt_claims = user_claims

    return encode_jwt(
        current_app.config["JWT_SECRET"], current_app.config["JWT_ALGORITHM"],
        current_app.config["ACCESS_TOKEN_DURATION"], jwt_claims), jti


def create_refresh_token(user_id, jti):
    """
    Creates refresh token, adds to database session, commit should be handled 
    outside function.

    :param user_id: user id
    :param jti: access token jti
    :returns refresh token string
    """

    token = str(uuid4())

    refresh_token = RefreshToken(
        token=token, user_id=user_id, access_token_jti=jti)

    db.session.add(refresh_token)
    db.session.commit()

    return refresh_token.token


def set_access_token_cookie(response, access_token):
    """
    Sets access token in cookie

    :param response: flask response object
    :param access_token: access token
    """

    now = datetime.utcnow()

    response.set_cookie(
        current_app.config["ACCESS_TOKEN_COOKIE_NAME"],
        access_token,
        secure=current_app.config["SECURE_TOKEN_COOKIES"],
        expires=now + current_app.config["REFRESH_TOKEN_DURATION"],
        httponly=True)


def set_refresh_token_cookie(response, refresh_token):
    """
    Sets refresh token in cookie

    :param response: flask response object
    :param refresh_token: refresh token
    """

    now = datetime.utcnow()

    response.set_cookie(
        current_app.config["REFRESH_TOKEN_COOKIE_NAME"],
        refresh_token,
        secure=current_app.config["SECURE_TOKEN_COOKIES"],
        expires=now + current_app.config["REFRESH_TOKEN_DURATION"],
        httponly=True)


def set_token_cookies(response, user_id):
    """
    Sets both token cookies

    :param respones: Flask response object
    :param user_id: user id to attatch to session
    """

    access_token, jti = create_access_token(user_id)

    refresh_token = create_refresh_token(user_id, jti)

    set_access_token_cookie(response, access_token)
    set_refresh_token_cookie(response, refresh_token)


def get_access_token_from_cookie():
    """
    Returns access token from the cookie
    """

    access_token = request.cookies[current_app.
                                   config["ACCESS_TOKEN_COOKIE_NAME"]]

    return access_token


def get_refresh_token_from_cookie():
    """
    Returns refresh token from the cookie
    """

    refresh_token = request.cookies[current_app.
                                    config["REFRESH_TOKEN_COOKIE_NAME"]]

    return refresh_token


def clear_token_cookies(response):
    """
    clears both token cookies

    :param response: Flask response object
    """

    access_cookie_name = current_app.config["ACCESS_TOKEN_COOKIE_NAME"]
    refresh_cookie_name = current_app.config["REFRESH_TOKEN_COOKIE_NAME"]
    secure_token_cookies = current_app.config["SECURE_TOKEN_COOKIES"]

    response.set_cookie(
        access_cookie_name,
        "",
        expires=0,
        secure=secure_token_cookies,
        httponly=True)
    response.set_cookie(
        refresh_cookie_name,
        "",
        expires=0,
        secure=secure_token_cookies,
        httponly=True)


def revoke_user_tokens(user_id):
    """
    Revokes all user refresh tokens

    :param user_id: id of the user
    """

    stmt = RefreshToken.__table__.update().where(
        and_(RefreshToken.__table__.c.user_id == user_id,
             RefreshToken.__table__.c.expires_at > datetime.utcnow(),
             RefreshToken.__table__.c.revoked == False)).values(revoked=True)

    db.session.execute(stmt)


def revoke_token(cls, token):
    """
    Revoke single token
    :param token: token object to be revoked
    """

    if token.is_valid():
        token.revoked = True

    db.session.commit()


# TODO: refactor, divide decorator
def authentication_required(f):
    """
    Checks access token validity
    """

    @wraps(f)
    def f_wrapper(*args, **kwargs):

        try:
            access_token = get_access_token_from_cookie()
        except KeyError:
            response = make_response(
                jsonify({
                    "message": "invalid token"
                }), 401)
            clear_token_cookies(response)
            clear_csrf_token_cookies(response)

            return response

        try:
            g.jwt_claims = decode_jwt(access_token,
                                      current_app.config["JWT_SECRET"],
                                      current_app.config["JWT_ALGORITHM"])
        except jwt.exceptions.ExpiredSignatureError:

            try:
                refresh_token = get_refresh_token_from_cookie()
            except KeyError:
                response = make_response(
                    jsonify({
                        "message": "invalid token"
                    }), 401)
                clear_token_cookies(response)
                clear_csrf_token_cookies(response)

                return response

            refresh_token = RefreshToken.first(token=refresh_token)

            if refresh_token is not None and refresh_token.is_valid():
                jwt_claims = decode_jwt(
                    access_token,
                    current_app.config["JWT_SECRET"],
                    current_app.config["JWT_ALGORITHM"],
                    options={"verify_exp": False})

                if not refresh_token.is_jti_valid(jwt_claims["jti"]):
                    # check if access token is blacklisted if it isn't
                    # jwt secret has been compromised

                    revoke_user_tokens(refresh_token.user_id)
                    db.session.commit()
                    response = make_response(
                        jsonify({
                            "message": "invalid token"
                        }), 401)
                    clear_token_cookies(response)
                    clear_csrf_token_cookies(response)

                    return response

                new_access_token, new_jti = create_access_token(
                    jwt_claims["user_id"], jwt_claims)
                refresh_token.access_token_jti = new_jti
                db.session.commit()

                g.new_access_token = new_access_token
                return f(*args, **kwargs)

            response = make_response(
                jsonify({
                    "message": "invalid token"
                }), 401)
            clear_token_cookies(response)
            clear_csrf_token_cookies(response)

            return response
        except jwt.exceptions.InvalidTokenError:
            response = make_response(
                jsonify({
                    "message": "invalid token"
                }), 401)
            clear_token_cookies(response)
            clear_csrf_token_cookies(response)

            return response

        return f(*args, **kwargs)

    return f_wrapper