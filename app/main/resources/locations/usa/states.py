from app.models.consolidated_city import ConsolidatedCity as CCModel
from app.models.county import County as CountyModel
from app.models.place import Place as PlaceModel
from app.models.state import State as StateModel

from flask import request
from flask_restful import Resource


class States(Resource):

  def get(self):
    states = StateModel.query.all()
    states_list = []
    for state in states:
      states_list.append(state.to_dict())

    return {"states": states_list}


class State(Resource):

  def get(self, fips_code=None):
    if fips_code is None:
      name = request.args.get("name", "", type=str)
      if not name:
        return {"message": "no name or fips_code provided"}, 404
      state = StateModel.query.filter(
          StateModel.name.like("%{}%".format(name))).first()
    else:
      state = StateModel.query.filter_by(fips_code=fips_code).first()

    if state is not None:
      return {"state": state.to_dict()}

    return {"state": {}}


class Counties(Resource):

  def get(self, state_fips=None):
    per_page = request.args.get("per_page", 15, type=int)
    page = request.args.get("page", 1, type=int)

    if state_fips is None:
      counties = CountyModel.query
      return {
          "counties":
              CountyModel.to_collection_dict(counties, page, per_page,
                                             "usa_state_counties")
      }
    else:
      state = StateModel.query.filter_by(fips_code=state_fips).first()
      if state is None:
        return {"message": "state not found"}, 404
      counties = state.counties
      return {
          "counties":
              CountyModel.to_collection_dict(
                  counties,
                  page,
                  per_page,
                  "usa_state_counties",
                  state_fips=state_fips)
      }


class Places(Resource):

  def get(self, state_fips=None):
    per_page = request.args.get("per_page", 15, type=int)
    page = request.args.get("page", 1, type=int)

    if state_fips is None:
      places = PlaceModel.query
      return {
          "places":
              PlaceModel.to_collection_dict(places, page, per_page,
                                            "usa_state_places")
      }
    else:
      state = StateModel.query.filter_by(fips_code=state_fips).first()
      if state is None:
        return {"message": "state not found"}, 404
      places = state.places
      return {
          "places":
              PlaceModel.to_collection_dict(
                  places,
                  page,
                  per_page,
                  "usa_state_places",
                  state_fips=state_fips)
      }


class ConsolidatedCities(Resource):

  def get(self, state_fips=None):
    per_page = request.args.get("per_page", 15, type=int)
    page = request.args.get("page", 1, type=int)

    if state_fips is None:
      return {
          "consolidated_cities":
              CCModel.to_collection_dict(CCModel.query, page, per_page,
                                         "usa_state_consolidated_cities")
      }
    else:
      state = StateModel.query.filter_by(fips_code=state_fips).first()
      if state is None:
        return {"message": "state not found"}, 404
      consolidated_cities = state.consolidated_cities
      return {
          "consolidated_cities":
              CCModel.to_collection_dict(
                  consolidated_cities,
                  page,
                  per_page,
                  "usa_state_consolidated_cities",
                  state_fips=state_fips)
      }
