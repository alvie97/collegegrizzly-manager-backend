"""Handles grade_requirement_groups

This module handles all related to grade requirement groups from creation to
deletion.

Attributes:
    bp: Flask blueprint
"""
import flask

bp = flask.Blueprint("grade_requirement_groups", __name__)

from . import routes
