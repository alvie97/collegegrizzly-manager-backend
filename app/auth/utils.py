import functools

import flask
import jwt

import app
from app.models import refresh_token
from app.security import token_auth


def user_not_logged(f):
    """Decorator to redirect if user is already logged in.

    Args:
        f: function to wrap.
    
    Returns:
        Function wrapper
    """

    @functools.wraps(f)
    def f_wrapper(*args, **kwargs):
        """Function wrapper

        Args:
            *args: variable length argument list.
            **kwargs: arbitrary keyword arguments.
        
        Returns:
            flask response or the wrapped function
        """
        try:
            access_token = token_auth.get_access_token_from_cookie()
        except KeyError:
            return f(*args, **kwargs)

        try:
            token_auth.decode_jwt(access_token,
                                  flask.current_app.config["JWT_SECRET"],
                                  flask.current_app.config["JWT_ALGORITHM"])
            return flask.jsonify({"message": "user already logged in"}), 403
        except jwt.ExpiredSignatureError:
            return flask.jsonify({"message": "user already logged in"}), 403
        except jwt.PyJWTError:
            return f(*args, **kwargs)

        return f(*args, **kwargs)

    return f_wrapper
