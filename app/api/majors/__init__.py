"""Handles majors"""

import flask

bp = flask.Blueprint("majors", __name__)

from . import routes