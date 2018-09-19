from flask import Blueprint
bp = Blueprint("colleges", __name__)

from . import routes
