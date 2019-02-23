import flask
import marshmallow

import app
from app import colleges as colleges_module
from app import security
from app import utils
from app.models import college as college_model
from app.models import consolidated_city as consolidated_city_model
from app.models import county as county_model
from app.models import major as major_model
from app.models import place as place_model
from app.models import scholarship as scholarship_model
from app.models import state as state_model
from app.schemas import college_schema
from app.schemas import major_schema as major_sc
from app.schemas import scholarship_schema

college_schema = college_schema.CollegeSchema()
major_schema = major_sc.MajorSchema()
majors_schema = major_sc.MajorSchema(many=True)
scholarship_schema = scholarship_schema.ScholarshipSchema()


@colleges_module.bp.route("/", methods=["GET"], strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_colleges():
    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["COLLEGES_PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = college_model.College.query.filter(
            college_model.College.name.like("%{}%".format(search)))

        data = college_model.College.to_collection_dict(
            query, page, per_page, "colleges.get_colleges", search=search)
    else:
        query = college_model.College.query
        data = college_model.College.to_collection_dict(
            query, page, per_page, "colleges.get_colleges")

    return flask.jsonify(data)


@colleges_module.bp.route("/", methods=["POST"], strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def post_college():
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        college = college_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    app.db.session.add(college)
    app.db.session.commit()

    return flask.jsonify({"college_id": college.public_id})


@colleges_module.bp.route("/<string:public_id>", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college(college):
    return flask.jsonify({"college": college.to_dict()})


@colleges_module.bp.route("/<string:public_id>", methods=["PATCH"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def patch_college(college):
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        college_schema.load(data, partial=True)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    college.update(data)
    app.db.session.commit()
    return flask.jsonify("college saved successfully")


@colleges_module.bp.route("/<string:public_id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college(college):
    college.delete()
    app.db.session.commit()

    return flask.jsonify({"message": "college deleted"})


@colleges_module.bp.route("/<string:public_id>/scholarships", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_scholarships(college):

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page",
        flask.current_app.config["SCHOLARSHIPS_PER_PAGE"],
        type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = college.scholarships.filter(
            scholarship_model.Scholarship.name.like("%{}%".format(search)))

        data = scholarship_model.Scholarship.to_collection_dict(
            query,
            page,
            per_page,
            "scholarships.get_scholarships",
            search=search)
    else:
        query = college.scholarships
        data = scholarship_model.Scholarship.to_collection_dict(
            query, page, per_page, "scholarships.get_scholarships")
    return flask.jsonify({"scholarships": data})


@colleges_module.bp.route("/<string:public_id>/scholarships", methods=["POST"])
@utils.get_entity(college_model.College, "public_id")
def post_college_scholarship(college):
    data = flask.request.get_json()

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        scholarship_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    scholarship = scholarship_model.Scholarship(
        public_id=utils.generate_public_id(), college=college, **data)

    app.db.session.add(scholarship)
    app.db.session.commit()

    return flask.jsonify({"scholarship_id": scholarship.public_id})


@colleges_module.bp.route("/<string:public_id>/majors", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_majors(college):
    return flask.jsonify({"majors": college.get_majors()})


@colleges_module.bp.route("/<string:public_id>/majors", methods=["POST"])
@utils.get_entity(college_model.College, "public_id")
def post_college_majors(college):
    data = flask.request.get_json() or {}

    if not data or "majors" not in data:
        return flask.jsonify({"message": "no data provided"}), 400

    for major in data["majors"]:

        try:
            major_schema.load(major)
        except marshmallow.ValidationError as err:
            return flask.jsonify(err.messages), 422

        major_to_add = major_model.Major.first(name=major["name"])

        if major_to_add is None:
            major_to_add = major_model.Major(**major)
            app.db.session.add(major_to_add)

        college.add_major(major_to_add)

    app.db.session.commit()
    return flask.jsonify({"message": "majors added"})


@colleges_module.bp.route("/<string:public_id>/majors", methods=["DELETE"])
@utils.get_entity(college_model.College, "public_id")
def delete_college_majors(college):
    data = flask.request.get_json() or {}

    if not data or "majors" not in data:
        return flask.jsonify({"message": "no data provided"}), 400

    for major in data["majors"]:
        major_to_remove = college.majors.filter_by(name=major).first()

        if major_to_remove is None:
            return flask.jsonify({
                "message":
                college.name + "doesn't have major " + major
            }), 404

        college.remove_major(major_to_remove)

    app.db.session.commit()
    return flask.jsonify({"message": "majors removed"})


@colleges_module.bp.route("/<string:public_id>/states", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_states(college):
    return utils.get_location_requirement(
        state_model.State,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route("/<string:public_id>/states", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_states(college):
    return utils.post_location_requirement(state_model.State, college)


@colleges_module.bp.route("/<string:public_id>/states", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_states(college):
    return utils.delete_location_requirement(state_model.State, college)


@colleges_module.bp.route("/<string:public_id>/counties", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_counties(college):
    return utils.get_location_requirement(
        county_model.County,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route("/<string:public_id>/counties", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_counties(college):
    return utils.post_location_requirement(county_model.County, college)


@colleges_module.bp.route("/<string:public_id>/counties", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_counties(college):
    return utils.delete_location_requirement(county_model.County, college)


@colleges_module.bp.route("/<string:public_id>/places", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_places(college):
    return utils.get_location_requirement(
        place_model.Place,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route("/<string:public_id>/places", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_places(college):
    return utils.post_location_requirement(place_model.Place, college)


@colleges_module.bp.route("/<string:public_id>/places", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_places(college):
    return utils.delete_location_requirement(place_model.Place, college)


@colleges_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_consolidated_cities(college):
    return utils.get_location_requirement(
        consolidated_city_model.ConsolidatedCity,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_consolidated_cities(college):
    return utils.post_location_requirement(
        consolidated_city_model.ConsolidatedCity, college)


@colleges_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_consolidated_cities(college):
    return utils.delete_location_requirement(
        consolidated_city_model.ConsolidatedCity, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_states_blacklist(college):
    return utils.get_locations_blacklist(
        state_model.State,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_states_blacklist(college):
    return utils.post_locations_blacklist(state_model.State, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_states_blacklist(college):
    return utils.delete_locations_blacklist(state_model.State, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_counties_blacklist(college):
    return utils.get_locations_blacklist(
        county_model.County,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_counties_blacklist(college):
    return utils.post_locations_blacklist(county_model.County, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_counties_blacklist(college):
    return utils.delete_locations_blacklist(county_model.County, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_places_blacklist(college):
    return utils.get_locations_blacklist(
        place_model.Place,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_places_blacklist(college):
    return utils.post_locations_blacklist(place_model.Place, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_places_blacklist(college):
    return utils.delete_locations_blacklist(place_model.Place, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_consolidated_cities_blacklist(college):
    return utils.get_locations_blacklist(
        consolidated_city_model.ConsolidatedCity,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_consolidated_cities_blacklist(college):
    return utils.post_locations_blacklist(
        consolidated_city_model.ConsolidatedCity, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_consolidated_cities_blacklist(college):
    return utils.delete_locations_blacklist(
        consolidated_city_model.ConsolidatedCity, college)


@colleges_module.bp.route("/majors_suggestions/<string:query>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def majors_suggestions(query):
    suggestions = major_model.Major.query.filter(
        major_model.Major.name.like(f"%{query}%")).limit(5).all()

    return flask.jsonify({
        "suggestions": [suggestion.to_dict() for suggestion in suggestions]
    })