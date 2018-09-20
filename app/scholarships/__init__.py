from flask import Blueprint

bp = Blueprint("scholarships", __name__)

from . import routes
