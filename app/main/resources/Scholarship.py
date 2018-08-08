from flask_restful import Resource
from flask import request
from app import db
from app.models.Scholarship import Scholarship as ScholarshipModel


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
