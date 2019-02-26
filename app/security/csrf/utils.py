from datetime import datetime, timedelta
from functools import wraps
from uuid import uuid4

from flask import current_app, jsonify, request


def generate_csrf_token():
    """ Generates csrf token and returns it """

    return str(uuid4())


def validate_csrf_token():
    """validates csrf token.

    Validates if CSRF cookie and header are valid and equal.

    Returns:
        bool: True if it's valid, False if not.
    """

    try:
        cookie_csrf_token = request.cookies[current_app.
                                            config["CSRF_COOKIE_NAME"]]
        header_csrf_token = request.headers[current_app.
                                            config["CSRF_HEADER_NAME"]]
    except KeyError:
        return False

    if not (cookie_csrf_token and header_csrf_token):
        return False

    if cookie_csrf_token != header_csrf_token:
        return False

    return True


def set_csrf_token_cookies(response, csrf_token):
    """Sets CSRF token to cookies.

    Args:
        response (Obj) (required): response object
        csrf_token: csrf token string.
    """
    response.set_cookie(
        current_app.config["CSRF_COOKIE_NAME"],
        csrf_token,
        secure=current_app.config["SECURE_TOKEN_COOKIES"],
        httponly=True,
        expires=datetime.utcnow() +
        current_app.config["REFRESH_TOKEN_DURATION"])

    response.set_cookie(
        current_app.config["CSRF_HEADER_NAME"],
        csrf_token,
        secure=current_app.config["SECURE_TOKEN_COOKIES"],
        expires=datetime.utcnow() +
        current_app.config["REFRESH_TOKEN_DURATION"])


def csrf_token_required(f):
    """Validates csrf token cookie and header, decorator.

    Response:
        obj: Flask response, a message and a 401 code if validation fails.
        f: if validation passes.
    """

    @wraps(f)
    def f_wrapper(*args, **kwargs):

        if not validate_csrf_token():
            return jsonify({"message": "unauthorized"}), 401

        return f(*args, **kwargs)

    return f_wrapper


def clear_csrf_token_cookies(response):
    """Clears csrf token cookies.

    Args:
        response (obj) (required): Flask response object
    """

    csrf_cookie_name = current_app.config["CSRF_COOKIE_NAME"]
    csrf_header_name = current_app.config["CSRF_HEADER_NAME"]
    secure_token_cookies = current_app.config["SECURE_TOKEN_COOKIES"]

    response.set_cookie(
        csrf_cookie_name,
        "",
        expires=0,
        secure=secure_token_cookies,
        httponly=True)

    response.set_cookie(
        csrf_header_name,
        "",
        expires=0,
        secure=secure_token_cookies,
        httponly=True)
