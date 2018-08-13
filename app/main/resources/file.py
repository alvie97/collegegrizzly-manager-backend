from flask_restful import Resource
from flask import send_from_directory
import os


class File(Resource):

  def get(self, folder, filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(
        os.path.join(root_dir, 'backend', 'static', folder), filename)
