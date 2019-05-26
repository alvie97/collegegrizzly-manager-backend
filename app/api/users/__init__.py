import flask

bp = flask.Blueprint("users", __name__)

from . import routes