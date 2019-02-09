from flask import current_app, request, jsonify
from marshmallow import ValidationError

from app import db
from app.models.college import College
from app.models.program import Program
from app.models.scholarship import Scholarship
from app.models.state import State
from app.models.county import County
from app.models.place import Place
from app.models.consolidated_city import ConsolidatedCity
from app.schemas.program_schema import ProgramSchema
from app.schemas.scholarship_schema import ScholarshipSchema
from app.common.utils import (
    generate_public_id, get_entity, get_location_requirement,
    post_location_requirement, delete_location_requirement,
    get_locations_blacklist, post_locations_blacklist,
    delete_locations_blacklist, get_first)
from app.security.utils import user_role, ADMINISTRATOR, MODERATOR, BASIC

from . import bp

scholarship_schema = ScholarshipSchema()
program_schema = ProgramSchema()

@bp.route("/", methods=["GET"], strict_slashes=False)
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_scholarships():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get(
        "per_page", current_app.config["SCHOLARSHIPS_PER_PAGE"], type=int)

    search = request.args.get("search", "", type=str)

    if search:
        query = Scholarship.query.filter(
            Scholarship.name.like("%{}%".format(search)))

        data = Scholarship.to_collection_dict(
            query,
            page,
            per_page,
            "scholarships.get_scholarships",
            search=search)
    else:
        query = Scholarship.query
        data = Scholarship.to_collection_dict(query, page, per_page,
                                              "scholarships.get_scholarships")

    return jsonify(data)

@bp.route("/<string:scholarship_id>")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship(scholarship):

    return jsonify({"scholarship": scholarship.to_dict()})


@bp.route("/<string:scholarship_id>", methods=["PATCH"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
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
    return jsonify("Scholarship saved successfully")


@bp.route("/<string:scholarship_id>", methods=["DELETE"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship(scholarship):

    db.session.delete(scholarship)
    db.session.commit()
    return jsonify({"message": "scholarship deleted"})

@bp.route("/<string:scholarship_id>/programs")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship_programs(scholarship):
    return jsonify({"programs": scholarship.get_programs()})


@bp.route("/<string:scholarship_id>/programs", methods=["POST"])
@get_entity(Scholarship, "scholarship")
def post_scholarship_programs(scholarship):
    program = request.get_json() or {}

    if not program:
        return jsonify({"message": "no data provided"}), 400

    try:
        program_schema.load(program)
    except ValidationError as err:
        return jsonify(err.messages), 422

    program_to_add = Program.first(
        name=program["name"],
        round_qualification=program["round_qualification"])

    if program_to_add is None:
        program_to_add = Program(**program)
        db.session.add(program_to_add)

    scholarship.add_program(program_to_add)

    db.session.commit()
    return jsonify({"message": "programs added"})


@bp.route("/<string:scholarship_id>/programs", methods=["DELETE"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_programs(scholarship):
    data = request.get_json() or {}

    if not data or "programs" not in data:
        return jsonify({"message": "no data provided"}), 400

    for program in data["programs"]:

        program_to_remove = scholarship.programs.filter_by(
            name=program["name"],
            round_qualification=program["round_qualification"]).first()

        if program_to_remove is not None:
            scholarship.remove_program(program_to_remove)

    db.session.commit()
    return jsonify({"message": "programs removed"})


@bp.route("/programs_suggestions/name/<string:query>")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def programs_suggestions_name(query):
    suggestions = Program.query.filter(
        Program.name.like(f"%{query}%")).limit(5).all()

    return jsonify({
        "suggestions": [suggestion.to_dict() for suggestion in suggestions]
    })


@bp.route("/programs_suggestions/round_qualification/<string:query>")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def programs_suggestions_round(query):
    suggestions = Program.query.filter(
        Program.round_qualification.like(f"%{query}%")).limit(5).all()

    return jsonify({
        "suggestions": [suggestion.to_dict() for suggestion in suggestions]
    })


@bp.route("/<string:scholarship_id>/scholarships_needed")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get(scholarship):

    return jsonify({
        "scholarships_needed": scholarship.get_scholarships_needed()
    })


@bp.route("/<string:scholarship_id>/scholarships_needed", methods=["POST"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
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
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
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


@bp.route("/<string:scholarship_id>/states", methods=["GET"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship_states(scholarship):

    return get_location_requirement(
        State,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)


@bp.route("/<string:scholarship_id>/states", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def post_scholarship_states(scholarship):
    return post_location_requirement(State, scholarship)


@bp.route("/<string:scholarship_id>/states", methods=["DELETE"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_states(scholarship):
    return delete_location_requirement(State, scholarship)


@bp.route("/<string:scholarship_id>/counties", methods=["GET"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship_counties(scholarship):

    return get_location_requirement(
        County,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)


@bp.route("/<string:scholarship_id>/counties", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def post_scholarship_counties(scholarship):
    return post_location_requirement(County, scholarship)


@bp.route("/<string:scholarship_id>/counties", methods=["DELETE"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_counties(scholarship):
    return delete_location_requirement(County, scholarship)


@bp.route("/<string:scholarship_id>/places", methods=["GET"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship_places(scholarship):

    return get_location_requirement(
        Place,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)


@bp.route("/<string:scholarship_id>/places", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def post_scholarship_places(scholarship):
    return post_location_requirement(Place, scholarship)


@bp.route("/<string:scholarship_id>/places", methods=["DELETE"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_places(scholarship):
    return delete_location_requirement(Place, scholarship)


@bp.route("/<string:scholarship_id>/consolidated_cities", methods=["GET"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship_consolidated_cities(scholarship):

    return get_location_requirement(
        ConsolidatedCity,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)


@bp.route("/<string:scholarship_id>/consolidated_cities", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def post_scholarship_consolidated_cities(scholarship):
    return post_location_requirement(ConsolidatedCity, scholarship)


@bp.route("/<string:scholarship_id>/consolidated_cities", methods=["DELETE"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_consolidated_cities(scholarship):
    return delete_location_requirement(ConsolidatedCity, scholarship)


@bp.route("/<string:scholarship_id>/blacklist/states", methods=["GET"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship_states_blacklist(scholarship):

    return get_locations_blacklist(
        State,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)


@bp.route("/<string:scholarship_id>/blacklist/states", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def post_scholarship_states_blacklist(scholarship):
    return post_locations_blacklist(State, scholarship)


@bp.route("/<string:scholarship_id>/blacklist/states", methods=["DELETE"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_states_blacklist(scholarship):
    return delete_locations_blacklist(State, scholarship)


@bp.route("/<string:scholarship_id>/blacklist/counties", methods=["GET"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship_counties_blacklist(scholarship):

    return get_locations_blacklist(
        County,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)


@bp.route("/<string:scholarship_id>/blacklist/counties", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def post_scholarship_counties_blacklist(scholarship):
    return post_locations_blacklist(County, scholarship)


@bp.route("/<string:scholarship_id>/blacklist/counties", methods=["DELETE"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_counties_blacklist(scholarship):
    return delete_locations_blacklist(County, scholarship)


@bp.route("/<string:scholarship_id>/blacklist/places", methods=["GET"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship_places_blacklist(scholarship):

    return get_locations_blacklist(
        Place,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)


@bp.route("/<string:scholarship_id>/blacklist/places", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def post_scholarship_places_blacklist(scholarship):
    return post_locations_blacklist(Place, scholarship)


@bp.route("/<string:scholarship_id>/blacklist/places", methods=["DELETE"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_places_blacklist(scholarship):
    return delete_locations_blacklist(Place, scholarship)


@bp.route(
    "/<string:scholarship_id>/blacklist/consolidated_cities", methods=["GET"])
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def get_scholarship_consolidated_cities_blacklist(scholarship):

    return get_locations_blacklist(
        ConsolidatedCity,
        "scholarships.scholarship",
        scholarship,
        scholarship_id=scholarship.public_id)


@bp.route(
    "/<string:scholarship_id>/blacklist/consolidated_cities", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def post_scholarship_consolidated_cities_blacklist(scholarship):
    return post_locations_blacklist(ConsolidatedCity, scholarship)


@bp.route(
    "/<string:scholarship_id>/blacklist/consolidated_cities",
    methods=["DELETE"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(Scholarship, "scholarship")
def delete_scholarship_consolidated_cities_blacklist(scholarship):
    return delete_locations_blacklist(ConsolidatedCity, scholarship)
