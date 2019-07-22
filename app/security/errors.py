import flask
import app


@app.jwt.expired_token_loader
def expired_token_loader(token):
    """If expired token attempts to access a protected route.

    Args:
        token: expired token.
    Returns:
        Object (Flask response): error message and code.
    """

    return flask.jsonify({"message": "expired token"}), 401


@app.jwt.invalid_token_loader
def invalid_token_loader(token):
    """If invalid token attempts to access a protected route.

    Args:
        token: invalid token.
    Returns:
        Object (Flask response): error message and code.
    """

    return flask.jsonify({"message": "invalid token"}), 422


@app.jwt.revoked_token_loader
def revoked_token_loader():
    """If revoked token attempts to access a protected route.

    Returns:
        Object (Flask response): error message and code.
    """

    return flask.jsonify({"message": "revoked token"}), 401


@app.jwt.unauthorized_loader
def unauthorized_loader(src):
    """If a not jwt attempts to access a protected route.
    Args:
        src: message with why a jwt was not found.
    Returns:
        Object (Flask response): error message and code.
    """

    return flask.jsonify({"message": "invalid token"}), 422