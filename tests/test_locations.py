# TODO: add tests for state counties, places and consolidated cities
from app.cli import _save_states
from app.models.college import College
from app.models.consolidated_city import ConsolidatedCity
from app.models.county import County
from app.models.place import Place
from app.models.scholarship import Scholarship
from app.models.state import State

url = "/api/locations"


def test_states(app, client, auth):

    with app.app_context():
        _save_states(2)

        db_states = State.query.all()

        auth.login()

        response = client.get(url + "/states")

        states = response.get_json()
        states = states["states"]["items"]

        for i, state in enumerate(states):
            assert state["name"] == db_states[i].name

        state = State.query.first()

        response = client.get(url + f"/states/{state.fips_code}")
        response_state = response.get_json()["state"]

        assert response_state["name"] == state.name


def test_counties(app, client, auth):

    with app.app_context():
        _save_states(1)
        db_counties = County.query.limit(5).all()

        auth.login()

        response = client.get(url + "/counties")

        counties = response.get_json()
        counties = counties["counties"]["items"]

        for i, county in enumerate(counties):
            assert county["name"] == db_counties[i].name


def test_places(app, client, auth):

    with app.app_context():
        _save_states(1)
        db_places = Place.query.limit(5).all()

        auth.login()

        response = client.get(url + "/places")

        places = response.get_json()
        places = places["places"]["items"]

        for i, place in enumerate(places):
            assert place["name"] == db_places[i].name


def test_consolidated_cities(app, client, auth):

    with app.app_context():
        _save_states(1)
        db_consolidated_cities = ConsolidatedCity.query.limit(5).all()

        auth.login()

        response = client.get(url + "/consolidated_cities")

        consolidated_cities = response.get_json()
        consolidated_cities = consolidated_cities["consolidated_cities"][
            "items"]

        for i, consolidated_city in enumerate(consolidated_cities):
            assert consolidated_city["name"] == db_consolidated_cities[i].name
