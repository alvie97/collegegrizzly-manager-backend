import os
from app import db
from app.models.State import State
from app.models.County import County
from app.models.Place import Place
from app.models.Consolidated_city import Consolidated_city
from scripts.us_states_prcss import process_fips_codes


def register(app):

  @app.cli.group()
  def geocodes():
    """ state, counties, places and consolidated cities commands """
    pass

  @geocodes.command()
  def save_in_database():
    GEOCODES_PATH = os.path.join(
        os.getcwd(), "static/files/geocodes/all-geocodes-v2016.xlsx")
    codes = process_fips_codes(GEOCODES_PATH)
    for state_code, state in codes.items():
      state_instance = State(name=state["name"], fips_code=state_code)
      db.session.add(state_instance)
      for county_code, county in state["counties"].items():
        county_instance = County(
            name=county["name"],
            state=state_instance,
            fips_code=state_code + county_code)
        db.session.add(county_instance)
      for place_code, place in state["places"].items():
        place_instance = Place(
            name=place["name"],
            state=state_instance,
            fips_code=state_code + place_code)
        db.session.add(place_instance)
      for consolidated_city_code, consolidated_city in state[
          "consolidated_cities"].items():
        consolidated_city_instance = Consolidated_city(
            name=consolidated_city["name"],
            state=state_instance,
            fips_code=state_code + consolidated_city_code)
        db.session.add(consolidated_city_instance)
    db.session.commit()
