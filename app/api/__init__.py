from flask          import Blueprint
from flask_restful  import Api

bp = Blueprint('api', __name__)
api = Api(bp)

from app.api.resources import College, Colleges, Scholarship, Scholarships

api.add_resource(College, '/colleges/<string:college_id>')
api.add_resource(Colleges, '/colleges')
api.add_resource(Scholarship, '/scholarship/<string:scholarship_id>')
api.add_resource(Scholarships,
                 '/scholarships',
                 '/colleges/<string:college_id>/scholarships')
