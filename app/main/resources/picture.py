from flask_restful import Resource
from flask import request, current_app
from app import db, photos
from app.models.college import College as CollegeModel
from app.models.picture import Picture as PictureModel
from app.common.utils import generate_public_id


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


class Pictures(Resource):

  def get(self, college_id=None):
    if college_id is not None:
      college = CollegeModel.query.filter_by(public_id=college_id).first()
      if college is None:
        return {'message': 'College not found'}, 404

      resources = college.Pictures.all()

      data = {'items': [item.to_dict() for item in resources]}

      return data

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get(
        'per_page', current_app.config['COLLEGES_PER_PAGE'], type=int)

    data = PictureModel.to_collection_dict(PictureModel.query, page, per_page,
                                           'pictures')

    return data

  def post(self, college_id):

    if 'picture' not in request.files:
      return {'message': 'file missing'}, 404

    college = CollegeModel.query.filter_by(public_id=college_id).first()

    if college is None:
      return {'message': 'college not found'}, 404

    filename = photos.save(request.files['picture'])
    data = request.get_json() or {}
    if 'type' not in data:
      data['type'] = 'campus'

    picture = PictureModel(
        public_id=generate_public_id(),
        name=filename,
        college=college,
        **data)
    db.session.add(picture)
    db.session.commit()

    return picture.public_id

  def delete(self):
    data = request.get_json() or {}

    pictures = PictureModel.query.filter(
        PictureModel.public_id.in_(data['ids'])).all()

    for picture in pictures:
      picture.delete()
    db.session.commit()

    return {'message': 'Pictures deleted'}
