"""Handles qualification rounds

This module handles all related to qualification_rounds from creation to deletion.

Attributes:
    bp: Flask blueprint
"""
import flask

bp = flask.Blueprint("qualification_rounds", __name__)

from . import routes
