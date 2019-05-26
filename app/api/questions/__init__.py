"""Handles questions

This module handles all related to questions from creation to deletion.

Attributes:
    bp: Flask blueprint
"""
import flask

bp = flask.Blueprint("questions", __name__)

from . import routes
