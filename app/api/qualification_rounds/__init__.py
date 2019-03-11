"""Handles qualification rounds

This module handles all related to qualification_rounds from creation to deletion.

Attributes:
    bp: Flask blueprint
"""
import flask
from app.security import token_auth
# from app.security import csrf

bp = flask.Blueprint("qualification_rounds", __name__)

@bp.before_request
# @csrf.csrf_token_required
@token_auth.authentication_required
def before_request():
    pass

@bp.after_request
def after_request(response):

    if hasattr(flask.g, "new_access_token") and flask.g.new_access_token:
        token_auth.set_access_token_cookie(response, flask.g.new_access_token)

    return response

from . import routes
