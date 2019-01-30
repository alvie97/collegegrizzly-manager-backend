import os

from flask import current_app, request, send_from_directory, jsonify
from . import bp
from app.security.utils import user_role, ADMINISTRATOR, MODERATOR, BASIC


@bp.route("/photos/<path:filename>")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_file(filename):
    file_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(file_path, '..', '..', 'static', 'photos')
    file_path = os.path.abspath(file_path)
    return send_from_directory(file_path, filename)
