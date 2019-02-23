from app import db
from app.models.consolidated_city import ConsolidatedCity
from app.models.county import County
from app.models.place import Place
from app.models.state import State
from app.scripts.us_states_prcss import process_fips_codes
import os


def _save_states(n_state):
    """Saves n states to database

    Saves n number states to database from spreadsheet file

    Args:
        n_state (int): number of states to save to the database
    """
    GEOCODES_PATH = os.path.join(
        os.getcwd(), "static/files/geocodes/all-geocodes-v2016.xlsx")

    codes = process_fips_codes(GEOCODES_PATH)
    it = 0
    for state_code, state in codes.items():
        if it >= n_state:
            break
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
            consolidated_city_instance = ConsolidatedCity(
                name=consolidated_city["name"],
                state=state_instance,
                fips_code=state_code + consolidated_city_code)
            db.session.add(consolidated_city_instance)
        it += 1
    db.session.commit()


def register(app):
    """Registers cli commands and groups

    Args:
        app: app instance
    """

    @app.cli.group()
    def geocodes():
        """Geocodes commands group"""
        pass

    #TODO: break function
    @geocodes.command()
    def save_in_database():
        """Saves states and it's locations into the database"""

        GEOCODES_PATH = os.path.join(
            os.getcwd(), "static/files/geocodes/all-geocodes-v2016.xlsx")
        print("MESSAGE:", " starting processing of file " + GEOCODES_PATH)
        codes = process_fips_codes(GEOCODES_PATH)
        print("MESSAGE: processing ended")
        print("MESSAGE: starting database data storage")
        for state_code, state in codes.items():
            print(
                "MESSAGE:", "starting storage of state {} in database".format(
                    state["name"]))
            state_instance = State(name=state["name"], fips_code=state_code)
            db.session.add(state_instance)
            c_count = 0
            for county_code, county in state["counties"].items():
                c_count += 1
                print(
                    "MESSAGE:",
                    "saving county {} of {}".format(c_count,
                                                    len(state["counties"])),
                    end='\r')
                county_instance = County(
                    name=county["name"],
                    state=state_instance,
                    fips_code=state_code + county_code)
                db.session.add(county_instance)
            print("")
            p_count = 0
            for place_code, place in state["places"].items():
                p_count += 1
                print(
                    "MESSAGE:",
                    "saving place {} of {}".format(p_count,
                                                   len(state["places"])),
                    end='\r')
                place_instance = Place(
                    name=place["name"],
                    state=state_instance,
                    fips_code=state_code + place_code)
                db.session.add(place_instance)
            print("")
            cc_count = 0
            for consolidated_city_code, consolidated_city in state[
                    "consolidated_cities"].items():
                cc_count += 1
                print(
                    "MESSAGE:",
                    "saving consolidated city {} of {}".format(
                        cc_count, len(state["consolidated_cities"])),
                    end='\r')
                consolidated_city_instance = ConsolidatedCity(
                    name=consolidated_city["name"],
                    state=state_instance,
                    fips_code=state_code + consolidated_city_code)
                db.session.add(consolidated_city_instance)
            print("")
        db.session.commit()
        print("SUCCESS:", " US locations data stored in the database")
