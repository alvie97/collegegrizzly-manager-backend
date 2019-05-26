"""Handles details

This module handles all related to details from creation to deletion.

Attributes:
    bp: Flask blueprint
"""
import flask

bp = flask.Blueprint("details", __name__)

from . import routes
