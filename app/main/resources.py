from flask_restful          import Resource
from flask                  import request, current_app
from app                    import db
from app.models.College     import College as CollegeModel
from app.models.Scholarship import Scholarship as ScholarshipModel
import uuid

class Colleges(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        data = CollegeModel.to_collection_dict(
                CollegeModel.query,
                page,
                current_app.config['COLLEGES_PER_PAGE'],
                'colleges')

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
    def get(self, college_id=None):
        if college_id is not None:
            college = CollegeModel.query.filter_by(public_id=college_id).first()
            if college is None:
                return {'message': 'College not found'}, 404

            page = request.args.get('page', 1, type=int)
            data = ScholarshipModel.to_collection_dict(
                college.Scholarships,
                paginate=False,
                college_id=college_id)

            return data

        page = request.args.get('page', 1, type=int)
        data = ScholarshipModel.to_collection_dict(ScholarshipModel.query, paginate=False)

        return data

    def post(self, college_id):
        college = CollegeModel.query.filter_by(public_id=college_id).first()

        if college is None:
            return {'message': 'college not found'}, 404

        data = request.get_json()

        scholarship = ScholarshipModel(
            public_id=str(uuid.uuid4()), college=college, **data)
        db.session.add(scholarship)
        db.session.commit()

        return scholarship.to_dict()

class Scholarship(Resource):
    def get(self, scholarship_id):
        scholarship = ScholarshipModel.query.filter_by(public_id=scholarship_id).first()

        if scholarship is None:
            return {'message': 'no scholarship found'}, 404

        return scholarship.to_dict()

    def put(self, scholarship_id):
        scholarship = ScholarshipModel.query.filter_by(public_id=scholarship_id).first()

        if scholarship is None:
            return {'message': 'no scholarship found'}, 404

        data = request.get_json()
        scholarship.from_dict({data['key']: data['val']})
        db.session.commit()
        return data;
