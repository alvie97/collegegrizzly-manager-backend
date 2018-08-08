from flask_restful import Resource
from flask import request
from app import db
from app.models.College import College as CollegeModel


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
