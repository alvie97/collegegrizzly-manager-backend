"""Handles qualification rounds

This module handles all related to options from creation to deletion.

Attributes:
    bp: Flask blueprint
"""
import flask

bp = flask.Blueprint("options", __name__)

from . import routes
