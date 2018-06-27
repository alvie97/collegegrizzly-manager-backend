from flask_restful      import Resource
from flask              import jsonify, request, current_app
from app                import db
from app.models.College import College as CollegeModel
from app.models.User    import User
import uuid

class Colleges(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        data = CollegeModel.to_collection_dict(CollegeModel.query,
                                    page,
                                    current_app.config['COLLEGES_PER_PAGE'],
                                    'api.colleges')
        return data

    def post(self):
        data = request.get_json() or {}

        college = CollegeModel(public_id=str(uuid.uuid4()), **data)

        db.session.add(college)
        db.session.commit()

        return college.to_dict()

class College(Resource):
    def get(self, college_id):
        college = CollegeModel.query.filter_by(public_id=college_id).first()

        if college is None:
            return {'message': 'no college found'}, 404

        return college.to_dict()

    def put(self, college_id):
        college = CollegeModel.query.filter_by(public_id=college_id).first()

        if college is None:
            return {'message': 'no college found'}, 404

        data = request.get_json() or {}

        college.from_dict(data)
        db.session.commit()
        return college.to_dict()

class Scholarships(Resource):
    def get(self):
        return {'message': 'get all scholarships'}

    def post(self, college_id):
        return {
            'message': 'create new scholarship for college {}'
                            .format(college_id)
        }

class Scholarship(Resource):
    def get(self, scholarship_id):
        return {'message': 'get scholarship {}'.format(scholarship_id)}

    def put(self, scholarship_id):
        return {'message': 'update scholarship {}'.format(scholarship_id)}
