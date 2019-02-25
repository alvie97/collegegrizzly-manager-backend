import flask
import marshmallow

import app
from app import scholarships as scholarships_module
from app import security, utils
from app.models import college as college_model
from app.models import consolidated_city as consolidated_city_model
from app.models import county as county_model
from app.models import place as place_model
from app.models import program as program_model
from app.models import scholarship as scholarship_model
from app.models import state as state_model
from app.schemas import program_schema, scholarship_schema

scholarship_schema = scholarship_schema.ScholarshipSchema()
program_schema = program_schema.ProgramSchema()


@scholarships_module.bp.route("/", methods=["GET"], strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_scholarships():
    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page",
        flask.current_app.config["SCHOLARSHIPS_PER_PAGE"],
        type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = scholarship_model.Scholarship.query.filter(
            scholarship_model.Scholarship.name.like("%{}%".format(search)))

        data = scholarship_model.Scholarship.to_collection_dict(
            query,
            page,
            per_page,
            "scholarships.get_scholarships",
            search=search)
    else:
        query = scholarship_model.Scholarship.query
        data = scholarship_model.Scholarship.to_collection_dict(
            query, page, per_page, "scholarships.get_scholarships")

    return flask.jsonify(data)


@scholarships_module.bp.route("/<string:public_id>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship(scholarship):

    return flask.jsonify({"scholarship": scholarship.to_dict()})


@scholarships_module.bp.route("/<string:public_id>", methods=["PATCH"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def patch_scholarship(scholarship):
    data = flask.request.get_json()

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        scholarship_schema.load(data, partial=True)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    scholarship.update(data)
    app.db.session.commit()
    return flask.jsonify("scholarship_model.Scholarship saved successfully")


@scholarships_module.bp.route("/<string:public_id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship(scholarship):

    app.db.session.delete(scholarship)
    app.db.session.commit()
    return flask.jsonify({"message": "scholarship deleted"})


@scholarships_module.bp.route("/<string:public_id>/programs")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_programs(scholarship):
    return flask.jsonify({"programs": scholarship.get_programs()})


@scholarships_module.bp.route("/<string:public_id>/programs", methods=["POST"])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_programs(scholarship):
    program = flask.request.get_json() or {}

    if not program:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        program_schema.load(program)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    program_to_add = program_model.Program.first(
        name=program["name"],
        round_qualification=program["round_qualification"])

    if program_to_add is None:
        program_to_add = program_model.Program(**program)
        app.db.session.add(program_to_add)

    scholarship.add_program(program_to_add)

    app.db.session.commit()
    return flask.jsonify({"message": "programs added"})


@scholarships_module.bp.route(
    "/<string:public_id>/programs", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_programs(scholarship):
    data = flask.request.get_json() or {}

    if not data or "programs" not in data:
        return flask.jsonify({"message": "no data provided"}), 400

    for program in data["programs"]:

        program_to_remove = scholarship.programs.filter_by(
            name=program["name"],
            round_qualification=program["round_qualification"]).first()

        if program_to_remove is not None:
            scholarship.remove_program(program_to_remove)

    app.db.session.commit()
    return flask.jsonify({"message": "programs removed"})


@scholarships_module.bp.route("/programs_suggestions/name/<string:query>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def programs_suggestions_name(query):
    suggestions = program_model.Program.query.filter(
        program_model.Program.name.like(f"%{query}%")).limit(5).all()

    return flask.jsonify({
        "suggestions": [suggestion.to_dict() for suggestion in suggestions]
    })


@scholarships_module.bp.route(
    "/programs_suggestions/round_qualification/<string:query>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def programs_suggestions_round(query):
    suggestions = program_model.Program.query.filter(
        program_model.Program.round_qualification.like(f"%{query}%")).limit(
            5).all()

    return flask.jsonify({
        "suggestions": [suggestion.to_dict() for suggestion in suggestions]
    })


@scholarships_module.bp.route("/<string:public_id>/scholarships_needed")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarships_needed(scholarship):

    return flask.jsonify({
        "scholarships_needed":
        scholarship.get_scholarships_needed()
    })


@scholarships_module.bp.route(
    "/<string:public_id>/scholarships_needed", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarships_needed(scholarship):
    data = flask.request.get_json() or {}

    if not data or "scholarships_needed" not in data:
        return flask.jsonify({"message": "no data provided"}), 400

    college = scholarship.college

    for scholarship_needed in data["scholarships_needed"]:
        if scholarship_needed == scholarship.public_id:
            continue

        scholarship_to_add = college.scholarships.filter_by(
            public_id=scholarship_needed).first()

        if scholarship_to_add is not None:
            scholarship.add_needed_scholarship(scholarship_to_add)

    app.db.session.commit()
    return flask.jsonify({"message": "needed scholarships added"})


@scholarships_module.bp.route(
    "/<string:public_id>/scholarships_needed", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarships_needed(scholarship):
    data = flask.request.get_json() or {}

    if not data or "scholarships_needed" not in data:
        return flask.jsonify({"message": "no data provided"}), 400

    for scholarship_needed in data["scholarships_needed"]:
        scholarship_to_remove = scholarship.scholarships_needed.filter_by(
            public_id=scholarship_needed).first()

        if scholarship_to_remove is not None:
            scholarship.remove_needed_scholarship(scholarship_to_remove)

    app.db.session.commit()
    return flask.jsonify({"message": "needed scholarships removed"})


@scholarships_module.bp.route("/<string:public_id>/states", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_states(scholarship):

    return utils.get_location_requirement(
        state_model.State,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route("/<string:public_id>/states", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_states(scholarship):
    return utils.post_location_requirement(state_model.State, scholarship)


@scholarships_module.bp.route("/<string:public_id>/states", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_states(scholarship):
    return utils.delete_location_requirement(state_model.State, scholarship)


@scholarships_module.bp.route("/<string:public_id>/counties", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_counties(scholarship):

    return utils.get_location_requirement(
        county_model.County,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route("/<string:public_id>/counties", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_counties(scholarship):
    return utils.post_location_requirement(county_model.County, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/counties", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_counties(scholarship):
    return utils.delete_location_requirement(county_model.County, scholarship)


@scholarships_module.bp.route("/<string:public_id>/places", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_places(scholarship):

    return utils.get_location_requirement(
        place_model.Place,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route("/<string:public_id>/places", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_places(scholarship):
    return utils.post_location_requirement(place_model.Place, scholarship)


@scholarships_module.bp.route("/<string:public_id>/places", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_places(scholarship):
    return utils.delete_location_requirement(place_model.Place, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_consolidated_cities(scholarship):

    return utils.get_location_requirement(
        consolidated_city_model.ConsolidatedCity,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_consolidated_cities(scholarship):
    return utils.post_location_requirement(
        consolidated_city_model.ConsolidatedCity, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_consolidated_cities(scholarship):
    return utils.delete_location_requirement(
        consolidated_city_model.ConsolidatedCity, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_states_blacklist(scholarship):

    return utils.get_locations_blacklist(
        state_model.State,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_states_blacklist(scholarship):
    return utils.post_locations_blacklist(state_model.State, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_states_blacklist(scholarship):
    return utils.delete_locations_blacklist(state_model.State, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_counties_blacklist(scholarship):

    return utils.get_locations_blacklist(
        county_model.County,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_counties_blacklist(scholarship):
    return utils.post_locations_blacklist(county_model.County, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_counties_blacklist(scholarship):
    return utils.delete_locations_blacklist(county_model.County, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_places_blacklist(scholarship):

    return utils.get_locations_blacklist(
        place_model.Place,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_places_blacklist(scholarship):
    return utils.post_locations_blacklist(place_model.Place, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_places_blacklist(scholarship):
    return utils.delete_locations_blacklist(place_model.Place, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_consolidated_cities_blacklist(scholarship):

    return utils.get_locations_blacklist(
        consolidated_city_model.ConsolidatedCity,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_consolidated_cities_blacklist(scholarship):
    return utils.post_locations_blacklist(
        consolidated_city_model.ConsolidatedCity, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_consolidated_cities_blacklist(scholarship):
    return utils.delete_locations_blacklist(
        consolidated_city_model.ConsolidatedCity, scholarship)
