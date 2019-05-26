"""Handles colleges

This module handles all related to colleges from creation to deletion.

Attributes:
    bp: Flask blueprint
"""
import flask

bp = flask.Blueprint("colleges", __name__)

from . import routes
