"""Handles programs

This module handles all related to programs from creation to deletion.

Attributes:
    bp: Flask blueprint
"""
import flask

bp = flask.Blueprint("programs", __name__)

from . import routes
