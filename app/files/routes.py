import os

from flask import current_app, request, send_from_directory, jsonify
from marshmallow import ValidationError

from app import db, photos
from app.common.utils import generate_public_id
from app.models.college import College
from app.models.picture import Picture

from . import bp


@bp.route("/<path:folder>/<path:filename>")
def get_file(folder, filename):
  root_dir = os.path.dirname(os.getcwd())
  return send_from_directory(
      os.path.join(root_dir, 'backend', 'static', folder), filename)


@bp.route("/pictures/<string:picture_id>")
def get_picture(picture_id):
  picture = Picture.first(public_id=picture_id)

  if picture is None:
    return jsonify({'message': 'no picture found'}), 404

  return jsonify(picture.to_dict())


@bp.route("/pictures/<string:picture_id>", methods=["PATCH"])
def patch_picture(picture_id):
  picture = Picture.first(public_id=picture_id)

  if picture is None:
    return jsonify({'message': 'no picture found'}), 404

  data = request.get_json()

  if data["key"] == "type" and data["value"] == "logo":
    college_logo = picture.college.pictures.filter_by(type="logo").first()

    if college_logo is not None:
      college_logo.update({'type': 'campus'})

  picture.update({data['key']: data['value']})
  db.session.commit()
  return jsonify(data)


@bp.route("/pictures/<string:picture_id>", methods=["DELETE"])
def delete_picture(picture_id):
  picture = Picture.query.filter_by(public_id=picture_id).first()

  if picture is None:
    return jsonify({'message': 'no picture found'}), 404

  db.session.delete(picture)
  db.session.commit()
  return jsonify({'message': 'picture deleted'})


@bp.route("/colleges/<string:college_id>/pictures")
@bp.route("/pictures")
def get_pictures(college_id=None):
  if college_id is not None:
    college = College.query.filter_by(public_id=college_id).first()
    if college is None:
      return jsonify({'message': 'College not found'}), 404

    resources = college.pictures.all()

    data = {'pictures': [item.to_dict() for item in resources]}

    return jsonify(data)

  page = request.args.get('page', 1, type=int)
  per_page = request.args.get(
      'per_page', current_app.config['COLLEGES_PER_PAGE'], type=int)

  data = Picture.to_collection_dict(Picture.query, page, per_page,
                                    'files.pictures')

  return jsonify(data)


@bp.route("/colleges/<string:college_id>/pictures", methods=["POST"])
def post_picture(college_id):

  if 'picture' not in request.files:
    return jsonify({'message': 'file missing'}), 404

  college = College.query.filter_by(public_id=college_id).first()

  if college is None:
    return jsonify({'message': 'college not found'}), 404

  filename = photos.save(request.files['picture'])
  data = request.get_json() or {}
  if 'type' not in data:
    data['type'] = 'campus'

  picture = Picture(
      public_id=generate_public_id(), name=filename, college=college, **data)
  db.session.add(picture)
  db.session.commit()

  return jsonify(picture.public_id)


@bp.route("/pictures", methods=["DELETE"])
def delete_pictures():
  data = request.get_json() or {}

  pictures = Picture.query.filter(Picture.public_id.in_(data['ids'])).all()

  for picture in pictures:
    picture.delete()
  db.session.commit()

  return jsonify({'message': 'Pictures deleted'})
