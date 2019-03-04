import flask


def bad_request(message):
    """Returns bad request error

    Args:
        message (string): error message.
    
    Returns:
        Object (Flask response): error code 400 and error message
    """

    return flask.jsonify({"message": message}), 400


def unauthorized(message):
    """Returns unauthorized error

    Args:
        message (string): error message.
    
    Returns:
        Object (Flask response): error code 401 and error message
    """

    return flask.jsonify({"message": message}), 401


def forbidden(message):
    """Returns unauthorized error

    Args:
        message (string): error message.
    
    Returns:
        Object (Flask response): error code 403 and error message
    """

    return flask.jsonify({"message": message}), 403