from flask import request, jsonify
from flask_restful import Resource

from app.models.consolidated_city import ConsolidatedCity as CC
from app.models.county import County
from app.models.place import Place
from app.models.state import State
from app.schemas.major_schema import MajorSchema

from . import bp


# TODO: change lazy to dynamic for pagination
@bp.route("/states")
def get_states():
  states = State.query.all()
  states_list = []
  for state in states:
    states_list.append(state.to_dict())

  return jsonify({"states": states_list})


@bp.route("/states/search/<string:name>")
def get_state_by_name(name):

  state = State.query.filter(
      State.name.like("%{}%".format(name))).first()

  if state is not None:
    return jsonify({"state": state.to_dict()})

  return jsonify({"message": "Not state found"}), 404

@bp.route("/states/<string:fips_code>")
def get_state(fips_code):

    state = State.query.filter_by(fips_code=fips_code).first()

  if state is not None:
    return jsonify({"state": state.to_dict()})

  return jsonify({"message": "state not found"}), 404

@bp.route("/states/<string:state_fips>/counties")
def get_counties(state_fips):
  per_page = request.args.get("per_page", 15, type=int)
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
              "get_state_counties",
              state_fips=state_fips)
  })


@bp.route("/states/<string:state_fips/places")
def get_state_places(state_fips=None):
  per_page = request.args.get("per_page", 15, type=int)
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
              "get_state_places",
              state_fips=state_fips)
  })


@bp.route("/states/<string:state_fips/consolidated_cities")
def get_state_consolidated_cities(state_fips):
  per_page = request.args.get("per_page", 15, type=int)
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
              "get_state_consolidated_cities",
              state_fips=state_fips)
  })

@bp.route("/counties")
def get_counties():
  per_page = request.args.get("per_page", 15, type=int)
  page = request.args.get("page", 1, type=int)

  return jsonify({
      "counties":
          County.to_collection_dict(County.query, page, per_page,
                                      "get_counties")
  })

@bp.route("/places")
def get_places():
  per_page = request.args.get("per_page", 15, type=int)
  page = request.args.get("page", 1, type=int)

  return jsonify({
      "places":
          Place.to_collection_dict(Place.query, page, per_page,
                                      "get_places")
  })

@bp.route("/consolidated_cities")
def get_consolidated_cities():
  per_page = request.args.get("per_page", 15, type=int)
  page = request.args.get("page", 1, type=int)

  return jsonify({
      "consolidated_cities":
          CC.to_collection_dict(CC.query, page, per_page,
                                      "get_consolidated_cities")
  })
