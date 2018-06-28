from flask  import Blueprint
from app    import api

bp = Blueprint('main', __name__)

from .resources import College, Colleges, Scholarship, Scholarships

api.add_resource(College, '/colleges/<string:college_id>', endpoint='college')
api.add_resource(Colleges, '/colleges', endpoint='colleges')
api.add_resource(Scholarship,
                 '/scholarships/<string:scholarship_id>',
                 endpoint='scholarship')
api.add_resource(Scholarships,
                 '/scholarships',
                 '/colleges/<string:college_id>/scholarships',
                 endpoint='scholarships')
