"""Server files manipulation

This module handles server files from storing to serving.
Attributes:
    bp: flask Blueprint
"""
import flask
bp = flask.Blueprint("files", __name__)

from . import routes