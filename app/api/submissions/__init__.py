"""Handles all submissions"""
import flask

bp = flask.Blueprint("submissions", __name__)

from . import routes