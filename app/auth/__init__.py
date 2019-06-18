"""Authentication.

Authenticates users to the applications and loggs them out.
"""
import flask

bp = flask.Blueprint("auth", __name__)

from . import routes