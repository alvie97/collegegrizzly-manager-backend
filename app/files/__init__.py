from flask import Blueprint
bp = Blueprint("files", __name__)

from . import routes