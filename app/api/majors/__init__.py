"""Handles majors

Attributes:
    bp: Flask blueprint
"""

import flask

bp = flask.Blueprint("majors", __name__)

from . import routes