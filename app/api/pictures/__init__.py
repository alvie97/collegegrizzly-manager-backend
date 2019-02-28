"""Handles pictures

Attributes:
    bp: Flask Blueprint.
"""
import flask
bp = flask.Blueprint("pictures", __name__)

from . import routes