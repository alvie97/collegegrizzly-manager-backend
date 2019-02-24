from decimal import Decimal

from app import db
from app.cli import _save_states
from app.utils import generate_public_id
from app.models.college import College

url = "/api/colleges"


def test_get_colleges(app, client, auth):
    """ get all colleges and test search function """

    # create colleges to test

    colleges_properties = []

    with app.app_context():
        for i in range(50):

            colleges_properties.append({"name": f"test college {i}"})

            college = College(**colleges_properties[i])
            db.session.add(college)

        db.session.commit()

    # login

    auth.login()

    # get colleges

    response = client.get(url)
    data = response.get_json()
    colleges = data["items"]

    for i, college in enumerate(colleges):
        assert college["name"] == colleges_properties[i]["name"]

    # get college that ends with "ge 2"

    response = client.get(url + "?search=ge 2")
    data = response.get_json()
    colleges = data["items"]

    for college in colleges:
        assert college["name"].find("ge 2") != -1


def test_crud_college(app, client, auth):
    """ create colleges and edit them"""

    auth.login()

    # create college

    data = {"name": "test post college"}

    response = client.post(url, json=data)

    response_data = response.get_json()

    college_id = response_data["college_id"]

    with app.app_context():
        college = College.first(public_id=college_id)

        assert college is not None

        for key, value in data.items():
            assert getattr(college, key) == value

    # read college

    response = client.get(url + f"/{college_id}")

    college_data = response.get_json()
    college_data = college_data["college"]["editable_fields"]

    with app.app_context():
        college = College.first(public_id=college_id)

        assert college is not None

        for key, value in college_data.items():
            college_value = getattr(college, key)
            if isinstance(college_value, Decimal):
                college_value = str(college_value)

            assert college_value == value

    # update college

    patch_data = {"name": "test patch college", "in_state_tuition": 1200}

    response = client.patch(url + f"/{college_id}", json=patch_data)

    with app.app_context():
        college = College.first(public_id=college_id)

        assert college is not None

        for key, value in patch_data.items():
            assert getattr(college, key) == value

    # delete college

    response = client.delete(url + f"/{college_id}")

    with app.app_context():
        college = College.first(public_id=college_id)

        assert college is None


def test_college_scholarships(app, client, auth):
    """ add college scholarships """

    with app.app_context():
        college = College(name="test college")
        db.session.add(college)
        db.session.commit()
        college_id = college.public_id

    auth.login()

    # add scholarships to college

    for i in range(3):
        client.post(
            url + f"/{college_id}/scholarships",
            json={"name": f"test scholarship {i}"})

    response = client.get(url + f"/{college_id}/scholarships")

    data = response.get_json()
    scholarships = data["scholarships"]["items"]

    for i, scholarship in enumerate(scholarships):
        assert f"test scholarship {i}" == scholarship["name"]


def test_college_majors(app, client, auth):
    """ add and delete college majors """

    with app.app_context():
        college = College(name="test college")
        db.session.add(college)
        db.session.commit()
        college_id = college.public_id

    majors_to_add = []

    for i in range(3):
        majors_to_add.append({
            "name": f"major {i}",
            "description": f"description of major {i}"
        })

    auth.login()

    client.post(url + f"/{college_id}/majors", json={"majors": majors_to_add})

    response = client.get(url + f"/{college_id}/majors")
    majors = response.get_json()
    majors = majors["majors"]

    for i, major in enumerate(majors):
        assert major["name"] == majors_to_add[i]["name"] and major[
            "description"] == majors_to_add[i]["description"]

    client.delete(url + f"/{college_id}/majors", json={"majors": ["major 0"]})

    response = client.get(url + f"/{college_id}/majors")
    majors = response.get_json()
    majors = majors["majors"]

    for i, major in enumerate(majors):
        assert major["name"] == majors_to_add[i + 1]["name"]


def test_college_states(app, client, auth):
    """ add, get and delete college states """

    with app.app_context():
        _save_states(5)

        college = College(name="test college")
        db.session.add(college)
        db.session.commit()
        college_id = college.public_id

    auth.login()

    response = client.get("/api/locations/states")

    states = response.get_json()
    states = states["states"]["items"]

    location_fips = []
    for state in states:
        location_fips.append(state["fips_code"])

    client.post(
        url + f"/{college_id}/states", json={"location_fips": location_fips})

    response = client.get(url + f"/{college_id}/states")
    states = response.get_json()
    states = states["states"]["items"]

    for i, state in enumerate(states):
        assert state["fips_code"] == location_fips[i]

    # delete college states

    client.delete(
        url + f"/{college_id}/states",
        json={"location_fips": [location_fips[0], location_fips[3]]})

    del location_fips[0]
    del location_fips[2]

    response = client.get(url + f"/{college_id}/states")
    states = response.get_json()
    states = states["states"]["items"]

    for i, state in enumerate(states):
        assert state["fips_code"] == location_fips[i]


def test_college_counties(app, client, auth):
    """ add, get and delete college counties """

    with app.app_context():
        _save_states(1)

        college = College(name="test college")
        db.session.add(college)
        db.session.commit()
        college_id = college.public_id

    auth.login()

    response = client.get("/api/locations/counties")

    counties = response.get_json()
    counties = counties["counties"]["items"]

    location_fips = []
    for county in counties:
        location_fips.append(county["fips_code"])

    client.post(
        url + f"/{college_id}/counties", json={"location_fips": location_fips})

    response = client.get(url + f"/{college_id}/counties")
    counties = response.get_json()
    counties = counties["counties"]["items"]

    for i, county in enumerate(counties):
        assert county["fips_code"] == location_fips[i]

    # delete college counties

    client.delete(
        url + f"/{college_id}/counties",
        json={"location_fips": [location_fips[0], location_fips[3]]})

    del location_fips[0]
    del location_fips[2]

    response = client.get(url + f"/{college_id}/counties")
    counties = response.get_json()
    counties = counties["counties"]["items"]

    for i, county in enumerate(counties):
        assert county["fips_code"] == location_fips[i]


def test_college_places(app, client, auth):
    """ add, get and delete college places """

    with app.app_context():
        _save_states(1)

        college = College(name="test college")
        db.session.add(college)
        db.session.commit()
        college_id = college.public_id

    auth.login()

    response = client.get("/api/locations/places")

    places = response.get_json()
    places = places["places"]["items"]

    location_fips = []
    for place in places:
        location_fips.append(place["fips_code"])

    client.post(
        url + f"/{college_id}/places", json={"location_fips": location_fips})

    response = client.get(url + f"/{college_id}/places")
    places = response.get_json()
    places = places["places"]["items"]

    for i, place in enumerate(places):
        assert place["fips_code"] == location_fips[i]

    # delete college places

    client.delete(
        url + f"/{college_id}/places",
        json={"location_fips": [location_fips[0], location_fips[3]]})

    del location_fips[0]
    del location_fips[2]

    response = client.get(url + f"/{college_id}/places")
    places = response.get_json()
    places = places["places"]["items"]

    for i, place in enumerate(places):
        assert place["fips_code"] == location_fips[i]


def test_college_consolidated_cities(app, client, auth):
    """ add, get and delete college consolidated_cities """

    with app.app_context():
        _save_states(14)

        college = College(name="test college")
        db.session.add(college)
        db.session.commit()
        college_id = college.public_id

    auth.login()

    response = client.get("/api/locations/consolidated_cities")

    consolidated_cities = response.get_json()
    consolidated_cities = consolidated_cities["consolidated_cities"]["items"]

    location_fips = []
    for consolidated_city in consolidated_cities:
        location_fips.append(consolidated_city["fips_code"])

    client.post(
        url + f"/{college_id}/consolidated_cities",
        json={"location_fips": location_fips})

    response = client.get(url + f"/{college_id}/consolidated_cities")
    consolidated_cities = response.get_json()
    consolidated_cities = consolidated_cities["consolidated_cities"]["items"]

    for i, consolidated_city in enumerate(consolidated_cities):
        assert consolidated_city["fips_code"] == location_fips[i]

    # delete college consolidated_cities

    client.delete(
        url + f"/{college_id}/consolidated_cities",
        json={"location_fips": [location_fips[0], location_fips[2]]})

    del location_fips[0]
    del location_fips[1]

    response = client.get(url + f"/{college_id}/consolidated_cities")
    consolidated_cities = response.get_json()
    consolidated_cities = consolidated_cities["consolidated_cities"]["items"]

    for i, consolidated_city in enumerate(consolidated_cities):
        assert consolidated_city["fips_code"] == location_fips[i]
