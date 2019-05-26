"""Handles grades

This module handles all related to grades from creation to deletion.

Attributes:
    bp: Flask blueprint
"""
import flask

bp = flask.Blueprint("grades", __name__)

from . import routes
