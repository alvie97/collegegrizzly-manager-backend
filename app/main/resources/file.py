import os

from flask import send_from_directory
from flask_restful import Resource
from marshmallow import ValidationError

from app.auth.csrf import csrf_token_required
from app.token_schema import access_token_required


class File(Resource):

  method_decorators = [csrf_token_required, access_token_required]

  def get(self, folder, filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(
        os.path.join(root_dir, 'backend', 'static', folder), filename)
