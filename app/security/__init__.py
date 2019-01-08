from flask import Blueprint

bp = Blueprint("security", __name__)

from . import routes