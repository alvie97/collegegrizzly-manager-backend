"""Handles scholarships

This module handles all related to scholarships from creation to deletion.

Attributes:
    bp: Flask blueprint
"""
import flask

bp = flask.Blueprint("scholarships", __name__)

from . import routes
