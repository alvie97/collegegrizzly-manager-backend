import os

from flask import current_app, request, send_from_directory, jsonify
from . import bp

from app.token_schema import access_token_required
from app.auth.csrf import csrf_token_required

@bp.before_request
@csrf_token_required
@access_token_required
def before_request():
  pass

@bp.route("/photos/<path:filename>")
def get_file(filename):
    file_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(file_path, '..', '..', 'static', 'photos')
    file_path = os.path.abspath(file_path)
    return send_from_directory(file_path, filename)
