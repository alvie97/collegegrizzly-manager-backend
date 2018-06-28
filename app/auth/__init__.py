from flask  import Blueprint
from app    import api

bp = Blueprint('auth', __name__)

from .resources import User, Users

api.add_resource(User, '/login', endpoint='user')
api.add_resource(Users, '/register', endpoint='users')
