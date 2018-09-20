from flask import jsonify, request, url_for, current_app
from marshmallow import ValidationError

from app import db
from app.models.college import College
from app.models.major import Major
from app.models.state import State
from app.models.county import County
from app.models.place import Place
from app.models.consolidated_city import ConsolidatedCity
from app.schemas.college_schema import CollegeSchema
from app.schemas.major_schema import MajorSchema
from app.common.utils import (generate_public_id, get_entity,
                              get_entity_of_resource, get_location_requirement,
                              post_location_requirement,
                              delete_location_requirement)

from . import bp

college_schema = CollegeSchema()
major_schema = MajorSchema()
majors_schema = MajorSchema(many=True)


@bp.route("/", methods=["GET"], strict_slashes=False)
def get_colleges():
  page = request.args.get("page", 1, type=int)
  per_page = request.args.get(
      "per_page", current_app.config["COLLEGES_PER_PAGE"], type=int)

  search = request.args.get("search", "", type=str)

  if search:
    query = College.query.filter(College.name.like("%{}%".format(search)))

    data = College.to_collection_dict(
        query, page, per_page, "colleges.get_colleges", search=search)
  else:
    query = College.query
    data = College.to_collection_dict(query, page, per_page, "colleges.get_colleges")

  return jsonify(data)


@bp.route("/", methods=["POST"], strict_slashes=False)
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


@bp.route("/<string:college_id>", methods=["GET"])
@get_entity(College, "college")
def get_college(college):
  return jsonify({"college": college.to_dict()})


@bp.route("/<string:college_id>", methods=["PATCH"])
@get_entity(College, "college")
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


@bp.route("/<string:college_id>", methods=["DELETE"])
@get_entity(College, "college")
def delete_college(college):
  college.delete()
  db.session.commit()

  return jsonify({"message": "college deleted"})


@bp.route("/<string:college_id>/scholarships", methods=["GET"])
@get_entity(College, "college")
def get_college_scholarships(college):

  return jsonify({
      "scholarships": [{
          "name":
              scholarship.name,
          "url":
              url_for(
                  "scholarships.get_scholarship",
                  scholarship_id=scholarship.public_id)
      } for scholarship in college.scholarships]
  })


@bp.route("/<string:college_id>/scholarships", methods=["POST"])
@get_entity(College, "college")
def post_scholarship(college):
  data = request.get_json()

  if not data:
    return jsonify({"message": "no data provided"}), 400

  try:
    scholarship_schema.load(data)
  except ValidationError as err:
    return jsonify(err.messages), 422

  scholarship = Scholarship(
      public_id=generate_public_id(), college=college, **data)

  db.session.add(scholarship)
  db.session.commit()

  return jsonify({"scholarship_id": scholarship.public_id})


@bp.route("/<string:college_id>/majors", methods=["GET"])
@get_entity(College, "college")
def get_college_majors(college):
  return jsonify({"majors": college.get_majors()})


@bp.route("/<string:college_id>/majors", methods=["POST"])
@get_entity(College, "college")
def post_college_majors(college):
  data = request.get_json() or {}

  if not data or "majors" not in data:
    return jsonify({"message": "no data provided"}), 400

  for major in data["majors"]:

    try:
      major_schema.load(major)
    except ValidationError as err:
      return jsonify(err.messages), 422

    major_to_add = Major.first(name=major["name"])

    if major_to_add is None:
      major_to_add = Major(**major)
      db.session.add(major_to_add)

    college.add_major(major_to_add)

  db.session.commit()
  return jsonify({"message": "majors added"})


@bp.route("/<string:college_id>/majors", methods=["DELETE"])
@get_entity(College, "college")
def delete_college_majors(college):
  data = request.get_json() or {}

  if not data or "majors" not in data:
    return jsonify({"message": "no data provided"}), 400

  for major in data["majors"]:
    major_to_remove = college.majors.filter_by(name=major).first()

    if major_to_remove is None:
      return jsonify({
          "message": college.name + "doesn't have major " + major
      }), 404

    college.remove_major(major_to_remove)

  db.session.commit()
  return jsonify({"message": "majors removed"})


@bp.route(
    "/<string:college_id>/states", methods=["GET", "POST", "PATCH", "DELETE"])
@get_entity_of_resource(College, "college")
def college_states(entity_obj):

  if request.method == "GET":
    return get_location_requirement(State, college, "college")

  if request.method == "POST":
    return post_location_requirement(State, college, "college")

  if request.method == "PATCH":
    return patch_location_requirement(State, college, "college")

  if request.method == "DELETE":
    return delete_location_requirement(State, college, "college")


@bp.route(
    "/<string:college_id>/counties",
    methods=["GET", "POST", "PATCH", "DELETE"])
@get_entity_of_resource(College, "college")
def college_counties(entity_obj):

  if request.method == "GET":
    return get_location_requirement(County, college, "college")

  if request.method == "POST":
    return post_location_requirement(County, college, "college")

  if request.method == "PATCH":
    return patch_location_requirement(County, college, "college")

  if request.method == "DELETE":
    return delete_location_requirement(County, college, "college")


@bp.route(
    "/<string:college_id>/places", methods=["GET", "POST", "PATCH", "DELETE"])
@get_entity_of_resource(College, "college")
def college_places(entity_obj):

  if request.method == "GET":
    return get_location_requirement(Place, college, "college")

  if request.method == "POST":
    return post_location_requirement(Place, college, "college")

  if request.method == "PATCH":
    return patch_location_requirement(Place, college, "college")

  if request.method == "DELETE":
    return delete_location_requirement(Place, college, "college")


@bp.route(
    "/<string:college_id>/consolidated_cities",
    methods=["GET", "POST", "PATCH", "DELETE"])
@get_entity_of_resource(College, "college")
def college_consolidated_cities(entity_obj):

  if request.method == "GET":
    return get_location_requirement(ConsolidatedCity, college, "college")

  if request.method == "POST":
    return post_location_requirement(ConsolidatedCity, college, "college")

  if request.method == "PATCH":
    return patch_location_requirement(ConsolidatedCity, college, "college")

  if request.method == "DELETE":
    return delete_location_requirement(ConsolidatedCity, college, "college")