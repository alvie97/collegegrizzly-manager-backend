from flask_restful import Resource
from flask import request
from app import db
from app.models.Picture import Picture as PictureModel


class Picture(Resource):

  def get(self, picture_id):
    picture = PictureModel.query.filter_by(public_id=picture_id).first()

    if picture is None:
      return {'message': 'no picture found'}, 404

    return picture.to_dict()

  def put(self, picture_id):
    picture = PictureModel.query.filter_by(public_id=picture_id).first()

    if picture is None:
      return {'message': 'no picture found'}, 404

    data = request.get_json()
    picture.from_dict({data['key']: data['value']})
    db.session.commit()
    return data

  def delete(self, picture_id):
    picture = PictureModel.query.filter_by(public_id=picture_id).first()

    if picture is None:
      return {'message': 'no picture found'}, 404

    db.session.delete(picture)
    db.session.commit()
    return {'message': 'picture deleted'}
