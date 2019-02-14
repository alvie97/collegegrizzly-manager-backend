from flask import Blueprint, g

bp = Blueprint("submissions", __name__)

from app.security.token_auth import (authentication_required,
                                     set_access_token_cookie)
from app.security.csrf import csrf_token_required


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


from . import routes
