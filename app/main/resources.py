from flask_restful          import Resource
from flask                  import request, current_app
from app                    import db
from app.models.College     import College as CollegeModel
from app.models.Scholarship import Scholarship as ScholarshipModel
import uuid

class Colleges(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get(
            'per_page', current_app.config['COLLEGES_PER_PAGE'], type=int)

        search = request.args.get('search', '', type=str)

        if search:
            query = CollegeModel.query.filter(
                CollegeModel.name.like('%{}%'.format(search)))
        else:
            query = CollegeModel.query

        data = CollegeModel.to_collection_dict(
                query,
                page,
                per_page,
                'colleges')

        return data

    def delete(self):
        data = request.get_json() or {}


        colleges = CollegeModel.query.filter(
            CollegeModel.public_id.in_(data['ids'])).all()

        for college in colleges:
            db.session.delete(college)

        db.session.commit()

        return {'message': 'Colleges deleted'}

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

        college.from_dict({data['key']: data['value']})
        db.session.commit()
        return college.to_dict()

class Scholarships(Resource):
    def get(self, college_id=None):
        if college_id is not None:
            college = CollegeModel.query.filter_by(public_id=college_id).first()
            if college is None:
                return {'message': 'College not found'}, 404

            data = ScholarshipModel.to_collection_dict(
                college.Scholarships,
                paginate=False,
                college_id=college_id)

            return data

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

        return scholarship.public_id

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
        scholarship.from_dict({data['key']: data['value']})
        db.session.commit()
        return data
    def delete(self, scholarship_id):
        scholarship = ScholarshipModel.query.filter_by(public_id=scholarship_id).first()

        if scholarship is None:
            return {'message': 'no scholarship found'}, 404

        db.session.delete(scholarship)
        db.session.commit()
        return {'message': 'scholarship deleted'}
