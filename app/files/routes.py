import os

from flask import current_app, request, send_from_directory
from flask_restful import Resource
from marshmallow import ValidationError

from app import db, photos
from app.common.utils import generate_public_id
from app.models.college import College as CollegeModel
from app.models.picture import Picture as PictureModel

from . import bp


@bp.route("/file/<path:folder>/<path:filename>")
def get_file(self, folder, filename):
  root_dir = os.path.dirname(os.getcwd())
  return send_from_directory(
      os.path.join(root_dir, 'backend', 'static', folder), filename)


@bp.route("/pictures/<string:picture_id>")
def get_picture(self, picture_id):
  picture = PictureModel.first(public_id=picture_id)

  if picture is None:
    return {'message': 'no picture found'}, 404

  return picture.to_dict()


@bp.route("/pictures/<string:picture_id>", methods=["PATCH"])
def patch_picture(self, picture_id):
  picture = PictureModel.first(public_id=picture_id)

  if picture is None:
    return {'message': 'no picture found'}, 404

  data = request.get_json()
  picture.update({data['key']: data['value']})
  db.session.commit()
  return data


@bp.route("/pictures/<string:picture_id>", methods=["DELETE"])
def delete_picture(self, picture_id):
  picture = PictureModel.query.filter_by(public_id=picture_id).first()

  if picture is None:
    return {'message': 'no picture found'}, 404

  db.session.delete(picture)
  db.session.commit()
  return {'message': 'picture deleted'}


@bp.route("/colleges/<string:college_id>/pictures")
@bp.route("/pictures")
def get_pictures(self, college_id=None):
  if college_id is not None:
    college = CollegeModel.query.filter_by(public_id=college_id).first()
    if college is None:
      return {'message': 'College not found'}, 404

    resources = college.pictures.all()

    data = {'items': [item.to_dict() for item in resources]}

    return data

  page = request.args.get('page', 1, type=int)
  per_page = request.args.get(
      'per_page', current_app.config['COLLEGES_PER_PAGE'], type=int)

  data = PictureModel.to_collection_dict(PictureModel.query, page, per_page,
                                         'pictures')

  return data


@bp.route("/colleges/<string:college_id>/pictures", methods=["POST"])
def post_picture(self, college_id):

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
      public_id=generate_public_id(), name=filename, college=college, **data)
  db.session.add(picture)
  db.session.commit()

  return picture.public_id


@bp.route("/pictures", methods=["DELETE"])
def delete_pictures(self):
  data = request.get_json() or {}

  pictures = PictureModel.query.filter(
      PictureModel.public_id.in_(data['ids'])).all()

  for picture in pictures:
    picture.delete()
  db.session.commit()

  return {'message': 'Pictures deleted'}
