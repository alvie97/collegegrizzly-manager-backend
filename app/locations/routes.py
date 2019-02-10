from flask import request, jsonify, current_app

from app.models.consolidated_city import ConsolidatedCity as CC
from app.models.county import County
from app.models.place import Place
from app.models.state import State
from app.security.utils import user_role, ADMINISTRATOR, MODERATOR, BASIC

from . import bp


# TODO: change lazy to dynamic for pagination
@bp.route("/states")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_states():
    per_page = request.args.get(
        "per_page", current_app.config["PER_PAGE"], type=int)
    page = request.args.get("page", 1, type=int)

    search = request.args.get("search", "", type=str)

    if search:
        query = State.query.filter(State.name.like("%{}%".format(search)))
        data = State.to_collection_dict(
            query, page, per_page, "locations.get_states", search=search)
    else:
        query = State.query
        data = State.to_collection_dict(query, page, per_page,
                                        "locations.get_states")

    return jsonify({"states": data})


@bp.route("/states/<string:fips_code>")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_state(fips_code):

    state = State.query.filter_by(fips_code=fips_code).first()

    if state is not None:
        return jsonify({"state": state.to_dict()})

    return jsonify({"message": "state not found"}), 404


@bp.route("/states/<string:state_fips>/counties")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_state_counties(state_fips):
    per_page = request.args.get(
        "per_page", current_app.config["PER_PAGE"], type=int)
    page = request.args.get("page", 1, type=int)

    state = State.query.filter_by(fips_code=state_fips).first()

    if state is None:
        return jsonify({"message": "state not found"}), 404
    counties = state.counties

    return jsonify({
        "counties":
        County.to_collection_dict(
            counties,
            page,
            per_page,
            "locations.get_state_counties",
            state_fips=state_fips)
    })


@bp.route("/states/<string:state_fips>/places")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_state_places(state_fips=None):
    per_page = request.args.get(
        "per_page", current_app.config["PER_PAGE"], type=int)
    page = request.args.get("page", 1, type=int)

    state = State.query.filter_by(fips_code=state_fips).first()
    if state is None:
        return jsonify({"message": "state not found"}), 404
    places = state.places
    return jsonify({
        "places":
        Place.to_collection_dict(
            places,
            page,
            per_page,
            "locations.get_state_places",
            state_fips=state_fips)
    })


@bp.route("/states/<string:state_fips>/consolidated_cities")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_state_consolidated_cities(state_fips):
    per_page = request.args.get(
        "per_page", current_app.config["PER_PAGE"], type=int)
    page = request.args.get("page", 1, type=int)

    state = State.query.filter_by(fips_code=state_fips).first()

    if state is None:
        return jsonify({"message": "state not found"}), 404
    consolidated_cities = state.consolidated_cities

    return jsonify({
        "consolidated_cities":
        CC.to_collection_dict(
            consolidated_cities,
            page,
            per_page,
            "locations.get_state_consolidated_cities",
            state_fips=state_fips)
    })


@bp.route("/counties")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_counties():
    per_page = request.args.get(
        "per_page", current_app.config["PER_PAGE"], type=int)
    page = request.args.get("page", 1, type=int)

    search = request.args.get("search", "", type=str)

    if search:
        query = County.query.filter(County.name.like("%{}%".format(search)))
        data = County.to_collection_dict(
            query, page, per_page, "locations.get_counties", search=search)
    else:
        query = County.query
        data = County.to_collection_dict(query, page, per_page,
                                         "locations.get_counties")

    return jsonify({"counties": data})


@bp.route("/places")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_places():
    per_page = request.args.get(
        "per_page", current_app.config["PER_PAGE"], type=int)
    page = request.args.get("page", 1, type=int)

    search = request.args.get("search", "", type=str)

    if search:
        query = Place.query.filter(Place.name.like("%{}%".format(search)))
        data = Place.to_collection_dict(
            query, page, per_page, "locations.get_places", search=search)
    else:
        query = Place.query
        data = Place.to_collection_dict(query, page, per_page,
                                        "locations.get_places")

    return jsonify({"places": data})


@bp.route("/consolidated_cities")
@user_role([ADMINISTRATOR, MODERATOR, BASIC])
def get_consolidated_cities():
    per_page = request.args.get(
        "per_page", current_app.config["PER_PAGE"], type=int)
    page = request.args.get("page", 1, type=int)

    search = request.args.get("search", "", type=str)

    if search:
        query = CC.query.filter(CC.name.like("%{}%".format(search)))
        data = CC.to_collection_dict(
            query,
            page,
            per_page,
            "locations.get_consolidated_cities",
            search=search)
    else:
        query = CC.query
        data = CC.to_collection_dict(query, page, per_page,
                                     "locations.get_consolidated_cities")

    return jsonify({"consolidated_cities": data})
