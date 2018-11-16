from flask import current_app, request, jsonify
from marshmallow import ValidationError

from app import db
from app.models.college import College
from app.models.ethnicity import Ethnicity
from app.models.program import Program
from app.models.scholarship import Scholarship
from app.models.state import State
from app.models.county import County
from app.models.place import Place
from app.models.consolidated_city import ConsolidatedCity
from app.schemas.ethnicity_schema import EthnicitySchema
from app.schemas.program_schema import ProgramSchema
from app.schemas.scholarship_schema import ScholarshipSchema
from app.common.utils import (
    generate_public_id, get_entity, get_location_requirement,
    post_location_requirement, delete_location_requirement,
    get_locations_blacklist, post_locations_blacklist,
    delete_locations_blacklist)
from app.token_schema import access_token_required
from app.auth.csrf import csrf_token_required

from . import bp

scholarship_schema = ScholarshipSchema()
program_schema = ProgramSchema()
ethnicity_schema = EthnicitySchema()


# @bp.before_request
# @csrf_token_required
# @access_token_required
# def before_request():
#   pass


@bp.route("/<string:scholarship_id>")
@get_entity(Scholarship, "scholarship")
def get_scholarship(scholarship):

  return jsonify({"scholarship": scholarship.to_dict()})


@bp.route("/<string:scholarship_id>", methods=["PATCH"])
@get_entity(Scholarship, "scholarship")
def patch_scholarship(scholarship):
  data = request.get_json()

  if not data:
    return jsonify({"message": "no data provided"}), 400

  try:
    scholarship_schema.load(data, partial=True)
  except ValidationError as err:
    return jsonify(err.messages), 422

  scholarship.update(data)
  db.session.commit()
  return jsonify({"scholarship": scholarship.to_dict()})


@bp.route("/<string:scholarship_id>", methods=["DELETE"])
@get_entity(Scholarship, "scholarship")
def delete_scholarship(scholarship):

  db.session.delete(scholarship)
  db.session.commit()
  return jsonify({"message": "scholarship deleted"})


@bp.route("/", methods=["GET"], strict_slashes=False)
def get_scholarships():
  page = request.args.get("page", 1, type=int)
  per_page = request.args.get(
      "per_page", current_app.config["SCHOLARSHIPS_PER_PAGE"], type=int)

  search = request.args.get("search", "", type=str)

  if search:
    query = Scholarship.query.filter(Scholarship.name.like("%{}%".format(search)))

    data = Scholarship.to_collection_dict(
        query, page, per_page, "scholarships.get_scholarships", search=search)
  else:
    query = Scholarship.query
    data = Scholarship.to_collection_dict(query, page, per_page,
                                      "scholarships.get_scholarships")

  return jsonify(data)


@bp.route("/<string:scholarship_id>/programs")
@get_entity(Scholarship, "scholarship")
def get_scholarship_majors(scholarship):
  return jsonify({"programs": scholarship.get_programs()})


@bp.route("/<string:scholarship_id>/programs", methods=["POST"])
@get_entity(Scholarship, "scholarship")
def post_scholarship_majors(scholarship):
  data = request.get_json() or {}

  if not data or "programs" not in data:
    return jsonify({"message": "no data provided"}), 400

  for program in data["programs"]:
    try:
      program_schema.load(program)
    except ValidationError as err:
      return jsonify(err.messages), 422

    program_to_add = Program.first(name=program["name"])

    if program_to_add is None:
      program_to_add = Program(**program)
      db.session.add(program_to_add)

    scholarship.add_program(program_to_add)

  db.session.commit()
  return jsonify({"message": "programs added"})


@bp.route("/<string:scholarship_id>/programs", methods=["DELETE"])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_majors(scholarship):
  data = request.get_json() or {}

  if not data or "programs" not in data:
    return jsonify({"message": "no data provided"}), 400

  for program in data["programs"]:
    program_to_remove = scholarship.programs.filter_by(name=program).first()

    if program_to_remove is None:
      return jsonify({
          "message": scholarship.name + "doesn't have program " + program
      }), 404

    scholarship.remove_program(program_to_remove)

  db.session.commit()
  return jsonify({"message": "programs removed"})


@bp.route("/<string:scholarship_id>/ethnicities")
@get_entity(Scholarship, "scholarship")
def get_scholarship_ethnicities(scholarship):
  return jsonify({"ethnicities": scholarship.get_ethnicities()})


@bp.route("/<string:scholarship_id>/ethnicities", methods=["POST"])
@get_entity(Scholarship, "scholarship")
def post_scholarship_ethnicities(scholarship):
  data = request.get_json() or {}

  if not data or "ethnicities" not in data:
    return jsonify({"message": "no data provided"}), 400

  for ethnicity in data["ethnicities"]:
    try:
      ethnicity_schema.load(ethnicity)
    except ValidationError as err:
      return jsonify(err.messages), 422

    ethnicity_to_add = Ethnicity.first(name=ethnicity["name"])

    if ethnicity_to_add is None:
      ethnicity_to_add = Ethnicity(**ethnicity)
      db.session.add(ethnicity_to_add)

    scholarship.add_ethnicity(ethnicity_to_add)

  db.session.commit()
  return jsonify({"message": "ethnicities added"})


@bp.route("/<string:scholarship_id>/ethnicities", methods=["DELETE"])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_ethnicities(scholarship):
  data = request.get_json() or {}

  if not data or "ethnicities" not in data:
    return jsonify({"message": "no data provided"}), 400

  for ethnicity in data["ethnicities"]:
    ethnicity_to_remove = scholarship.ethnicities.filter_by(
        name=ethnicity).first()

    if ethnicity_to_remove is None:
      return jsonify({
          "message": scholarship.name + "doesn't have ethnicity " + ethnicity
      }), 404

    scholarship.remove_ethnicity(ethnicity_to_remove)

  db.session.commit()
  return jsonify({"message": "ethnicities removed"})


@bp.route("/<string:scholarship_id>/scholarships_needed")
@get_entity(Scholarship, "scholarship")
def get(scholarship):

  return jsonify({
      "scholarships_needed": scholarship.get_scholarships_needed()
  })


@bp.route("/<string:scholarship_id>/scholarships_needed", methods=["POST"])
@get_entity(Scholarship, "scholarship")
def post(scholarship):
  data = request.get_json() or {}

  if not data or "scholarships_needed" not in data:
    return jsonify({"message": "no data provided"}), 400

  college = scholarship.college

  for scholarship_needed in data["scholarships_needed"]:
    if scholarship_needed == scholarship.public_id:
      continue

    scholarship_to_add = college.scholarships.filter_by(
        public_id=scholarship_needed).first()

    if scholarship_to_add is not None:
      scholarship.add_needed_scholarship(scholarship_to_add)

  db.session.commit()
  return jsonify({"message": "needed scholarships added"})


@bp.route("/<string:scholarship_id>/scholarships_needed", methods=["DELETE"])
@get_entity(Scholarship, "scholarship")
def delete(scholarship):
  data = request.get_json() or {}

  if not data or "scholarships_needed" not in data:
    return jsonify({"message": "no data provided"}), 400

  for scholarship_needed in data["scholarships_needed"]:
    scholarship_to_remove = scholarship.scholarships_needed.filter_by(
        public_id=scholarship_needed).first()

    if scholarship_to_remove is not None:
      scholarship.remove_needed_scholarship(scholarship_to_remove)

  db.session.commit()
  return jsonify({"message": "needed scholarships removed"})


@bp.route("/<string:scholarship_id>/states", methods=["GET", "POST", "DELETE"])
@get_entity(Scholarship, "scholarship")
def scholarship_states(scholarship):

  if request.method == "GET":
    return get_location_requirement(
        State,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)

  if request.method == "POST":
    return post_location_requirement(State, scholarship)

  if request.method == "DELETE":
    return delete_location_requirement(State, scholarship)


@bp.route(
    "/<string:scholarship_id>/counties", methods=["GET", "POST", "DELETE"])
@get_entity(Scholarship, "scholarship")
def scholarship_counties(scholarship):

  if request.method == "GET":
    return get_location_requirement(
        County,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)

  if request.method == "POST":
    return post_location_requirement(County, scholarship)

  if request.method == "DELETE":
    return delete_location_requirement(County, scholarship)


@bp.route("/<string:scholarship_id>/places", methods=["GET", "POST", "DELETE"])
@get_entity(Scholarship, "scholarship")
def scholarship_places(scholarship):

  if request.method == "GET":
    return get_location_requirement(
        Place,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)

  if request.method == "POST":
    return post_location_requirement(Place, scholarship)

  if request.method == "DELETE":
    return delete_location_requirement(Place, scholarship)


@bp.route(
    "/<string:scholarship_id>/consolidated_cities",
    methods=["GET", "POST", "DELETE"])
@get_entity(Scholarship, "scholarship")
def scholarship_consolidated_cities(scholarship):

  if request.method == "GET":
    return get_location_requirement(
        ConsolidatedCity,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)

  if request.method == "POST":
    return post_location_requirement(ConsolidatedCity, scholarship)

  if request.method == "DELETE":
    return delete_location_requirement(ConsolidatedCity, scholarship)


@bp.route(
    "/<string:scholarship_id>/blacklist/states",
    methods=["GET", "POST", "DELETE"])
@get_entity(Scholarship, "scholarship")
def scholarship_states_blacklist(scholarship):

  if request.method == "GET":
    return get_locations_blacklist(
        State,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)

  if request.method == "POST":
    return post_locations_blacklist(State, scholarship)

  if request.method == "DELETE":
    return delete_locations_blacklist(State, scholarship)


@bp.route(
    "/<string:scholarship_id>/blacklist/counties",
    methods=["GET", "POST", "DELETE"])
@get_entity(Scholarship, "scholarship")
def scholarship_counties_blacklist(scholarship):

  if request.method == "GET":
    return get_locations_blacklist(
        County,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)

  if request.method == "POST":
    return post_locations_blacklist(County, scholarship)

  if request.method == "DELETE":
    return delete_locations_blacklist(County, scholarship)


@bp.route(
    "/<string:scholarship_id>/blacklist/places",
    methods=["GET", "POST", "DELETE"])
@get_entity(Scholarship, "scholarship")
def scholarship_places_blacklist(scholarship):

  if request.method == "GET":
    return get_locations_blacklist(
        Place,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)

  if request.method == "POST":
    return post_locations_blacklist(Place, scholarship)

  if request.method == "DELETE":
    return delete_locations_blacklist(Place, scholarship)


@bp.route(
    "/<string:scholarship_id>/blacklist/consolidated_cities",
    methods=["GET", "POST", "DELETE"])
@get_entity(Scholarship, "scholarship")
def scholarship_consolidated_cities_blacklist(scholarship):

  if request.method == "GET":
    return get_locations_blacklist(
        ConsolidatedCity,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)

  if request.method == "POST":
    return post_locations_blacklist(ConsolidatedCity, scholarship)

  if request.method == "DELETE":
    return delete_locations_blacklist(ConsolidatedCity, scholarship)