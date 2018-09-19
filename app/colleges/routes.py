from flask import jsonify, request
from marshmallow import ValidationError

from app import db
from app.auth.csrf import csrf_token_required
from app.common.utils import get_entity
from app.models.college import College as CollegeModel
from app.models.major import Major as MajorModel
from app.schemas.college_schema import CollegeSchema
from app.schemas.major_schema import MajorSchema
from app.token_schema import access_token_required

from . import bp

college_schema = CollegeSchema()
major_schema = MajorSchema()
majors_schema = MajorSchema(many=True)


@bp.route("/", methods=["GET"])
def get_colleges():
  page = request.args.get("page", 1, type=int)
  per_page = request.args.get(
      "per_page", current_app.config["COLLEGES_PER_PAGE"], type=int)

  search = request.args.get("search", "", type=str)

  if search:
    query = CollegeModel.query.filter(
        CollegeModel.name.like("%{}%".format(search)))

    data = CollegeModel.to_collection_dict(
        query, page, per_page, "colleges", search=search)
  else:
    query = CollegeModel.query
    data = CollegeModel.to_collection_dict(query, page, per_page, "colleges")

  return jsonify(data)


@bp.route("/", methods=["POST"])
def post_college():
  data = request.get_json() or {}

  if not data:
    return jsonify({"message": "no data provided"}), 400

  try:
    college = college_schema.load(data)
  except ValidationError as err:
    return jsonify(err.messages), 422

  db.session.add(college)
  db.session.commit()

  return jsonify({"college_id": college.public_id})


@bp.route("/<string:id>", methods=["GET"])
@get_entity(CollegeModel, "college")
def get_college(college):
  return jsonify({"college": college.to_dict()})


@bp.route("/<string:id>", methods=["PATCH"])
@get_entity(CollegeModel, "college")
def patch_college(college):
  data = request.get_json() or {}

  if not data:
    return jsonify({"message": "no data provided"}), 400

  try:
    college_schema.load(data, partial=True)
  except ValidationError as err:
    return jsonify(err.messages), 422

  college.update(data)
  db.session.commit()
  return jsonify({"college": college.to_dict()})


@bp.route("/<string:id>", methods=["DELETE"])
@get_entity(CollegeModel, "college")
def delete_college(college):
  college.delete()
  db.session.commit()

  return jsonify({"message": "college deleted"})


@bp.route("/<string:id>/scholarships", methods=["GET"])
@get_entity(CollegeModel, "college")
def get_college_scholarships(college):

  return jsonify({
      "scholarships": [{
          "name": scholarship.name,
          "url": url_for(
              "scholarship", scholarship_id=scholarship.public_id)
      } for scholarship in college.scholarships]
  })


@bp.route("/<string:id>/majors", methods=["GET"])
@get_entity(CollegeModel, "college")
def get_college_majors(college):
  return jsonify({"majors": college.get_majors()})

@bp.route("/<string:id>/majors", methods=["POST"])
@get_entity(CollegeModel, "college")
def post_college_majors(college):
  data = request.get_json() or {}

  if not data or "majors" not in data:
    return jsonify({"message": "no data provided"}), 400

  for major in data["majors"]:

    try:
      major_schema.load(major)
    except ValidationError as err:
      return jsonify(err.messages), 422

    major_to_add = MajorModel.first(name=major["name"])

    if major_to_add is None:
      major_to_add = MajorModel(**major)
      db.session.add(major_to_add)

    college.add_major(major_to_add)

  db.session.commit()
  return jsonify({"message": "majors added"})


@bp.route("/<string:id>/majors", methods=["DELETE"])
@get_entity(CollegeModel, "college")
def delete_college_majors(college):
  data = request.get_json() or {}

  if not data or "majors" not in data:
    return jsonify({"message": "no data provided"}), 400

  for major in data["majors"]:
    major_to_remove = college.majors.filter_by(name=major).first()

    if major_to_remove is None:
      return jsonify({"message": college.name + "doesn't have major " + major}), 404

    college.remove_major(major_to_remove)

  db.session.commit()
  return jsonify({"message": "majors removed"})
