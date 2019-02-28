from flask import Blueprint, g

from app.security.csrf import csrf_token_required
from app.security.token_auth import (authentication_required,
                                     set_access_token_cookie)

from . import routes

bp = Blueprint("users", __name__)


@bp.before_request
# @csrf_token_required
@authentication_required
def before_request():
    pass


@bp.after_request
def after_request(response):

    if hasattr(g, "new_access_token") and g.new_access_token:
        set_access_token_cookie(response, g.new_access_token)

    return response
