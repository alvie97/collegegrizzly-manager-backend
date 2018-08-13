from flask_restful import Resource
from flask import request, current_app
from app import db
from app.models.scholarship import Scholarship as ScholarshipModel
from app.models.college import College as CollegeModel
from app.common.utils import generate_public_id


class Scholarship(Resource):

  def get(self, scholarship_id):
    scholarship = ScholarshipModel.query.filter_by(
        public_id=scholarship_id).first()

    if scholarship is None:
      return {'message': 'no scholarship found'}, 404

    return scholarship.to_dict()

  def put(self, scholarship_id):
    scholarship = ScholarshipModel.query.filter_by(
        public_id=scholarship_id).first()

    if scholarship is None:
      return {'message': 'no scholarship found'}, 404

    data = request.get_json()
    scholarship.from_dict({data['key']: data['value']})
    db.session.commit()
    return data

  def delete(self, scholarship_id):
    scholarship = ScholarshipModel.query.filter_by(
        public_id=scholarship_id).first()

    if scholarship is None:
      return {'message': 'no scholarship found'}, 404

    db.session.delete(scholarship)
    db.session.commit()
    return {'message': 'scholarship deleted'}


class Scholarships(Resource):

  def get(self, college_id=None):
    if college_id is not None:
      college = CollegeModel.query.filter_by(public_id=college_id).first()
      if college is None:
        return {'message': 'College not found'}, 404

      resources = college.Scholarships.all()
      data = {'items': [item.to_dict() for item in resources]}

      return data

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get(
        'per_page', current_app.config['SCHOLARSHIPS_PER_PAGE'], type=int)

    data = ScholarshipModel.to_collection_dict(ScholarshipModel.query, page,
                                               per_page, 'scholarships')

    return data

  def post(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()

    if college is None:
      return {'message': 'college not found'}, 404

    data = request.get_json()

    scholarship = ScholarshipModel(
        public_id=generate_public_id(), college=college, **data)
    db.session.add(scholarship)
    db.session.commit()

    return scholarship.public_id
