"""Handles locations

Searches and retrieves locations.

Attributes:
    bp: flask Blueprint
"""
import flask

bp = flask.Blueprint("locations", __name__)

from . import routes