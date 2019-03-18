import flask


class LocationEntityError(Exception):
    pass


def error_404(e):
    return flask.jsonify({"message": "resource not found"}), 404
