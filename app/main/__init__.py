from flask import Blueprint
from app   import api

bp = Blueprint('main', __name__)

from .resources.College      import College
from .resources.Colleges     import Colleges
from .resources.Scholarship  import Scholarship
from .resources.Scholarships import Scholarships
from .resources.Picture      import Picture
from .resources.Pictures     import Pictures

api.add_resource(College, '/colleges/<string:college_id>', endpoint='college')
api.add_resource(Colleges, '/colleges', endpoint='colleges')
api.add_resource(Scholarship,
                 '/scholarships/<string:scholarship_id>',
                 endpoint='scholarship')
api.add_resource(Scholarships,
                 '/scholarships',
                 '/colleges/<string:college_id>/scholarships',
                 endpoint='scholarships')
api.add_resource(Picture,
                 '/pictures/<string:picture_id>',
                 endpoint='picture')
api.add_resource(Pictures,
                 '/pictures',
                 '/colleges/<string:college_id>/pictures',
                 endpoint='pictures')
