from flask import Blueprint
bp = Blueprint("pictures", __name__)

from . import routes