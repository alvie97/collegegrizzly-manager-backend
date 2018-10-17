from flask import jsonify, request, url_for, current_app
from marshmallow import ValidationError

from app import db
from app.models.college import College
from app.models.scholarship import Scholarship
from app.models.major import Major
from app.models.state import State
from app.models.county import County
from app.models.place import Place
from app.models.consolidated_city import ConsolidatedCity
from app.schemas.college_schema import CollegeSchema
from app.schemas.scholarship_schema import ScholarshipSchema
from app.schemas.major_schema import MajorSchema
from app.common.utils import (
    generate_public_id, get_entity, get_location_requirement,
    post_location_requirement, delete_location_requirement,
    get_locations_blacklist, post_locations_blacklist,
    delete_locations_blacklist)

from app.token_schema import access_token_required
from app.auth.csrf import csrf_token_required

from . import bp

college_schema = CollegeSchema()
major_schema = MajorSchema()
majors_schema = MajorSchema(many=True)
scholarship_schema = ScholarshipSchema()

# @bp.before_request
# @csrf_token_required
# @access_token_required
# def before_request():
#   pass


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
    data = College.to_collection_dict(query, page, per_page,
                                      "colleges.get_colleges")

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
  return jsonify("college saved successfully")


@bp.route("/<string:college_id>", methods=["DELETE"])
@get_entity(College, "college")
def delete_college(college):
  college.delete()
  db.session.commit()

  return jsonify({"message": "college deleted"})


@bp.route("/<string:college_id>/scholarships", methods=["GET"])
@get_entity(College, "college")
def get_college_scholarships(college):

  page = request.args.get("page", 1, type=int)
  per_page = request.args.get(
      "per_page", current_app.config["SCHOLARSHIPS_PER_PAGE"], type=int)

  search = request.args.get("search", "", type=str)

  if search:
    query = college.scholarships.filter(
        Scholarship.name.like("%{}%".format(search)))

    data = Scholarship.to_collection_dict(
        query, page, per_page, "scholarships.get_scholarships", search=search)
  else:
    query = college.scholarships
    data = Scholarship.to_collection_dict(query, page, per_page,
                                          "scholarships.get_scholarships")
  return jsonify({"scholarships": data})


@bp.route("/<string:college_id>/scholarships", methods=["POST"])
@get_entity(College, "college")
def post_college_scholarship(college):
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


@bp.route("/<string:college_id>/states", methods=["GET", "POST", "DELETE"])
@get_entity(College, "college")
def college_states(college):

  if request.method == "GET":
    return get_location_requirement(
        State, "colleges.college", college, college_id=college.public_id)

  if request.method == "POST":
    return post_location_requirement(State, college)

  if request.method == "DELETE":
    return delete_location_requirement(State, college)


@bp.route("/<string:college_id>/counties", methods=["GET", "POST", "DELETE"])
@get_entity(College, "college")
def college_counties(college):

  if request.method == "GET":
    return get_location_requirement(
        County, "colleges.college", college, college_id=college.public_id)

  if request.method == "POST":
    return post_location_requirement(County, college)

  if request.method == "DELETE":
    return delete_location_requirement(County, college)


@bp.route("/<string:college_id>/places", methods=["GET", "POST", "DELETE"])
@get_entity(College, "college")
def college_places(college):

  if request.method == "GET":
    return get_location_requirement(
        Place, "colleges.college", college, college_id=college.public_id)

  if request.method == "POST":
    return post_location_requirement(Place, college)

  if request.method == "DELETE":
    return delete_location_requirement(Place, college)


@bp.route(
    "/<string:college_id>/consolidated_cities",
    methods=["GET", "POST", "DELETE"])
@get_entity(College, "college")
def college_consolidated_cities(college):

  if request.method == "GET":
    return get_location_requirement(
        ConsolidatedCity,
        "colleges.college",
        college,
        college_id=college.public_id)

  if request.method == "POST":
    return post_location_requirement(ConsolidatedCity, college)

  if request.method == "DELETE":
    return delete_location_requirement(ConsolidatedCity, college)


@bp.route(
    "/<string:college_id>/blacklist/states", methods=["GET", "POST", "DELETE"])
@get_entity(College, "college")
def college_states_blacklist(college):

  if request.method == "GET":
    return get_locations_blacklist(
        State, "colleges.college", college, college_id=college.public_id)

  if request.method == "POST":
    return post_locations_blacklist(State, college)

  if request.method == "DELETE":
    return delete_locations_blacklist(State, college)


@bp.route(
    "/<string:college_id>/blacklist/counties",
    methods=["GET", "POST", "DELETE"])
@get_entity(College, "college")
def college_counties_blacklist(college):

  if request.method == "GET":
    return get_locations_blacklist(
        County, "colleges.college", college, college_id=college.public_id)

  if request.method == "POST":
    return post_locations_blacklist(County, college)

  if request.method == "DELETE":
    return delete_locations_blacklist(County, college)


@bp.route(
    "/<string:college_id>/blacklist/places", methods=["GET", "POST", "DELETE"])
@get_entity(College, "college")
def college_places_blacklist(college):

  if request.method == "GET":
    return get_locations_blacklist(
        Place, "colleges.college", college, college_id=college.public_id)

  if request.method == "POST":
    return post_locations_blacklist(Place, college)

  if request.method == "DELETE":
    return delete_locations_blacklist(Place, college)


@bp.route(
    "/<string:college_id>/blacklist/consolidated_cities",
    methods=["GET", "POST", "DELETE"])
@get_entity(College, "college")
def college_consolidated_cities_blacklist(college):

  if request.method == "GET":
    return get_locations_blacklist(
        ConsolidatedCity,
        "colleges.college",
        college,
        college_id=college.public_id)

  if request.method == "POST":
    return post_locations_blacklist(ConsolidatedCity, college)

  if request.method == "DELETE":
    return delete_locations_blacklist(ConsolidatedCity, college)


@bp.route("/get_fields")
def college_get_fields():
  return jsonify({"fields": College.get_fields()})


@bp.route("/majors_suggestions/<string:query>")
def majors_suggestions(query):
  suggestions = Major.query.filter(
      Major.name.like(f"%{query}%")).limit(5).all()

  return jsonify({
      "suggestions": [suggestion.name for suggestion in suggestions]
  })
