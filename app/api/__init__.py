from flask import Blueprint
from flask_restful import Api

bp = Blueprint('api', __name__)
api = Api(bp)

from app.api.resources import College, Colleges, Scholarship, Scholarships

api.add_resource(College, '/colleges/<int:college_id>')
api.add_resource(Colleges, '/colleges/')
api.add_resource(Scholarship, '/scholarship/<int:scholarship_id>')
api.add_resource(Scholarships, '/scholarships/',
                '/colleges/<int:college_id>/scholarships')
