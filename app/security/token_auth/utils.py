import base64
import datetime
import functools
import uuid
import jwt
import flask
import sqlalchemy

import app
from app.models import refresh_token as refresh_token_model
from app.security import csrf


def encode_jwt(secret, algorithm, duration, additional_claims=None):
    """Encodes (utf-8) JWT.

    Args:
        secret (string) (required): key used to sign the token.
        algorithm (string) (required): algorithm to sign the token.
        duration (:obj datetime.timedelta): time until the token expires.
        additional_claims (dict): any additional claims to provide to the token.
    Returns:
        String: encoded jwt string (utf-8)
    """
    now = datetime.datetime.utcnow()

    claims = {"iat": now, "exp": now + duration}

    if additional_claims is not None:
        claims.update(additional_claims)

    return jwt.encode(claims, secret, algorithm=algorithm).decode("utf-8")


def decode_jwt(token, secret, algorithm, options=None):
    """Decodes JWT and validates if its valid.

    Args:
        token (string) (required): JWT to decode.
        secret (string) (required): secret used to verify signature.
        algorithm (string) (required): algorithm used to sign JWT.
        options (dict) (optional): jwt options dictionary.
    Returns:
        dict: jwt claims.
    """
    if options is not None:
        return jwt.decode(
            token, secret, algorithms=[algorithm], options=options)

    return jwt.decode(token, secret, algorithms=[algorithm])


def create_access_token(user_id, user_claims=None):
    """Creates access token.

    Args:
        user_id (integer) (required): id of user who owns this token. 
            can be any identifier like a username, email, uuid, etc.
        user_claims (dict) (optional): additional claims to encode in jwt.
    Returns:
        string: encoded jwt string (utf-8).
    """

    jti = str(uuid.uuid4())
    jwt_claims = {"user_id": user_id, "jti": jti}

    if user_claims is not None:
        user_claims.update(jwt_claims)
        jwt_claims = user_claims

    return encode_jwt(flask.current_app.config["JWT_SECRET"],
                      flask.current_app.config["JWT_ALGORITHM"],
                      flask.current_app.config["ACCESS_TOKEN_DURATION"],
                      jwt_claims), jti


def create_refresh_token(user_id, jti):
    """Creates refresh token.

    Creates refresh token, adds to database session, commit should be handled 
    outside function.

    Args:
        user_id (int) (required): user id.
        jti (string) (required): access token jti.
    Returns:
        string: refresh token string
    """

    token = str(uuid.uuid4())

    refresh_token = refresh_token_model.RefreshToken(
        token=token, user_id=user_id, access_token_jti=jti)

    app.db.session.add(refresh_token)
    app.db.session.commit()

    return refresh_token.token


def set_access_token_cookie(response, access_token):
    """Sets access token in cookie.

    Args:
        response (obj) (required): flask response object
        access_token (string) (required): access token
    """

    now = datetime.datetime.utcnow()

    response.set_cookie(
        flask.current_app.config["ACCESS_TOKEN_COOKIE_NAME"],
        access_token,
        secure=flask.current_app.config["SECURE_TOKEN_COOKIES"],
        expires=now + flask.current_app.config["REFRESH_TOKEN_DURATION"],
        httponly=True)


def set_refresh_token_cookie(response, refresh_token):
    """Sets refresh token in cookie.

    Args:
        response (ob) (required): flask response object
        refresh_token (string) (required): refresh token
    """

    now = datetime.datetime.utcnow()

    response.set_cookie(
        flask.current_app.config["REFRESH_TOKEN_COOKIE_NAME"],
        refresh_token,
        secure=flask.current_app.config["SECURE_TOKEN_COOKIES"],
        expires=now + flask.current_app.config["REFRESH_TOKEN_DURATION"],
        httponly=True)


def set_token_cookies(response, user_id, user_role):
    """Sets both token cookies

    Args:
        respone (obj) (required): Flask response object
        user_id (integer) (required): user id to attatch to session
        user_role (string) (required): role of the user
    """

    access_token, jti = create_access_token(
        user_id, user_claims={"role": user_role})

    refresh_token = create_refresh_token(user_id, jti)

    set_access_token_cookie(response, access_token)
    set_refresh_token_cookie(response, refresh_token)


def get_access_token_from_cookie():
    """Returns access token from the cookie"""

    access_token = flask.request.cookies[flask.current_app.
                                         config["ACCESS_TOKEN_COOKIE_NAME"]]

    return access_token


def get_refresh_token_from_cookie():
    """Returns refresh token from the cookie"""

    refresh_token = flask.request.cookies[flask.current_app.
                                          config["REFRESH_TOKEN_COOKIE_NAME"]]

    return refresh_token


def clear_token_cookies(response):
    """Clears both token cookies.

    Args:
        response (obj) (required): Flask response object
    """

    access_cookie_name = flask.current_app.config["ACCESS_TOKEN_COOKIE_NAME"]
    refresh_cookie_name = flask.current_app.config["REFRESH_TOKEN_COOKIE_NAME"]
    secure_token_cookies = flask.current_app.config["SECURE_TOKEN_COOKIES"]

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
    """Revokes all user refresh tokens.

    Args:
        user_id (integer) (required): id of the user.
    """

    stmt = refresh_token_model.RefreshToken.__table__.update().where(
        sqlalchemy.and_(
            refresh_token_model.RefreshToken.__table__.c.user_id == user_id,
            refresh_token_model.RefreshToken.__table__.c.expires_at >
            datetime.datetime.utcnow(), refresh_token_model.RefreshToken.
            __table__.c.revoked == False)).values(revoked=True)

    app.db.session.execute(stmt)


def revoke_token(cls, token):
    """Revoke single token

    Args:
        token (obj: RefreshToken): token object to be revoked
    """

    if token.is_valid():
        token.revoked = True

    app.db.session.commit()


# TODO: refactor, divide decorator
def authentication_required(f):
    """Checks access token validity.
    
        Returns:
            Obj Flask response: returns message and 401 if tokens are not valid.
            f: if tokens are valid.
    """

    @functools.wraps(f)
    def f_wrapper(*args, **kwargs):

        try:
            access_token = get_access_token_from_cookie()
        except KeyError:
            response = flask.make_response(
                flask.jsonify({
                    "message": "invalid token"
                }), 401)
            clear_token_cookies(response)
            csrf.clear_csrf_token_cookies(response)

            return response

        try:
            flask.g.jwt_claims = decode_jwt(
                access_token, flask.current_app.config["JWT_SECRET"],
                flask.current_app.config["JWT_ALGORITHM"])
        except jwt.exceptions.ExpiredSignatureError:

            try:
                refresh_token = get_refresh_token_from_cookie()
            except KeyError:
                response = flask.make_response(
                    flask.jsonify({
                        "message": "invalid token"
                    }), 401)
                clear_token_cookies(response)
                csrf.clear_csrf_token_cookies(response)

                return response

            refresh_token = refresh_token_model.RefreshToken.first(
                token=refresh_token)

            if refresh_token is not None and refresh_token.is_valid():
                jwt_claims = decode_jwt(
                    access_token,
                    flask.current_app.config["JWT_SECRET"],
                    flask.current_app.config["JWT_ALGORITHM"],
                    options={"verify_exp": False})

                if not refresh_token.is_jti_valid(jwt_claims["jti"]):
                    # check if access token is blacklisted if it isn't
                    # jwt secret has been compromised

                    revoke_user_tokens(refresh_token.user_id)
                    app.db.session.commit()
                    response = flask.make_response(
                        flask.jsonify({
                            "message": "invalid token"
                        }), 401)
                    clear_token_cookies(response)
                    csrf.clear_csrf_token_cookies(response)

                    return response

                new_access_token, new_jti = create_access_token(
                    jwt_claims["user_id"], jwt_claims)
                refresh_token.access_token_jti = new_jti
                app.db.session.commit()

                flask.g.new_access_token = new_access_token
                return f(*args, **kwargs)

            response = flask.make_response(
                flask.jsonify({
                    "message": "invalid token"
                }), 401)
            clear_token_cookies(response)
            csrf.clear_csrf_token_cookies(response)

            return response
        except jwt.exceptions.InvalidTokenError:
            response = flask.make_response(
                flask.jsonify({
                    "message": "invalid token"
                }), 401)
            clear_token_cookies(response)
            csrf.clear_csrf_token_cookies(response)

            return response

        return f(*args, **kwargs)

    return f_wrapper
