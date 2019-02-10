from app.common.utils import generate_public_id
from app import db
from app.models.scholarship import Scholarship
from app.models.college import College
from decimal import Decimal
from app.cli import _save_states

url = "/api/scholarships"


def test_get_scholarships(app, client, auth):
    """ get all scholarships and test search function """

    # add scholarships to database
    scholarships_properties = []

    with app.app_context():
        for i in range(50):

            scholarships_properties.append({"name": f"test scholarship {i}"})

            scholarship = Scholarship(**scholarships_properties[i])
            db.session.add(scholarship)

        db.session.commit()

    # login

    auth.login()

    # get scholarships

    response = client.get(url)
    data = response.get_json()
    scholarships = data["items"]

    for i, scholarship in enumerate(scholarships):
        assert scholarship["name"] == scholarships_properties[i]["name"]

    # get scholarship that ends with "ge 2"

    response = client.get(url + "?search=ship 2")
    data = response.get_json()
    scholarships = data["items"]

    for scholarship in scholarships:
        assert scholarship["name"].find("ship 2") != -1


def test_crud_scholarship(app, client, auth):
    """ read and edit scholarships"""

    with app.app_context():

        scholarship = Scholarship(name="test scholarship")
        db.session.add(scholarship)
        db.session.commit()
        scholarship_id = scholarship.public_id

    auth.login()

    # read scholarship

    response = client.get(url + f"/{scholarship_id}")

    scholarship_data = response.get_json()
    scholarship_data = scholarship_data["scholarship"]["editable_fields"]

    with app.app_context():
        scholarship = Scholarship.first(public_id=scholarship_id)

        assert scholarship is not None

        for key, value in scholarship_data.items():
            scholarship_value = getattr(scholarship, key)
            if isinstance(scholarship_value, Decimal):
                scholarship_value = str(scholarship_value)

            assert scholarship_value == value

    # update scholarship

    patch_data = {"name": "test patch scholarship"}

    response = client.patch(url + f"/{scholarship_id}", json=patch_data)

    with app.app_context():
        scholarship = Scholarship.first(public_id=scholarship_id)

        assert scholarship is not None

        for key, value in patch_data.items():
            assert getattr(scholarship, key) == value

    # delete scholarship

    response = client.delete(url + f"/{scholarship_id}")

    with app.app_context():
        scholarship = Scholarship.first(public_id=scholarship_id)

        assert scholarship is None


def test_scholarship_programs(app, client, auth):
    """ add and delete scholarship programs """

    with app.app_context():
        scholarship = Scholarship(name="test scholarship")
        db.session.add(scholarship)
        db.session.commit()
        scholarship_id = scholarship.public_id

    programs_to_add = []

    for i in range(3):
        programs_to_add.append({
            "name":
            f"program {i}",
            "round_qualification":
            f"round qualification of program {i}"
        })

    auth.login()

    client.post(
        url + f"/{scholarship_id}/programs",
        json={"programs": programs_to_add})

    response = client.get(url + f"/{scholarship_id}/programs")
    programs = response.get_json()
    programs = programs["programs"]

    for i, program in enumerate(programs):
        assert program["name"] == programs_to_add[i]["name"] and program[
            "round_qualification"] == programs_to_add[i]["round_qualification"]

    client.delete(
        url + f"/{scholarship_id}/programs",
        json={"programs": [programs_to_add[0]]})

    response = client.get(url + f"/{scholarship_id}/programs")
    programs = response.get_json()
    programs = programs["programs"]

    del programs_to_add[0]

    for i, program in enumerate(programs):
        assert program["name"] == programs_to_add[i]["name"] and program[
            "qualification_round"] == programs_to_add[i]


def test_scholarships_needed(app, client, auth):
    """ add and delete scholarships needed """

    with app.app_context():
        college = College(name="test college")
        db.session.add(college)
        scholarship_1 = Scholarship(name="test scholarship 1", college=college)
        scholarship_2 = Scholarship(name="test scholarship 2", college=college)
        db.session.add(scholarship_1)
        db.session.add(scholarship_2)
        db.session.commit()
        scholarship_id_1 = scholarship_1.public_id
        scholarship_id_2 = scholarship_2.public_id

    auth.login()

    client.post(
        url + f"/{scholarship_id_1}/scholarships_needed",
        json={"scholarships_needed": [scholarship_id_1, scholarship_id_2]})

    response = client.get(url + f"/{scholarship_id_1}/scholarships_needed")
    scholarships_needed = response.get_json()
    scholarships_needed = scholarships_needed["scholarships_needed"]

    assert len(scholarships_needed) == 1
    assert scholarships_needed[0]["public_id"] == scholarship_id_2

    client.delete(
        url + f"/{scholarship_id_1}/scholarships_needed",
        json={"scholarships_needed": [scholarship_id_2]})

    response = client.get(url + f"/{scholarship_id_1}/scholarships_needed")
    scholarships_needed = response.get_json()
    scholarships_needed = scholarships_needed["scholarships_needed"]

    assert len(scholarships_needed) == 0


def test_scholarship_states(app, client, auth):
    """ add, get and delete scholarship states """

    with app.app_context():
        _save_states(5)

        scholarship = Scholarship(name="test scholarship")
        db.session.add(scholarship)
        db.session.commit()
        scholarship_id = scholarship.public_id

    auth.login()

    response = client.get("/api/locations/states")

    states = response.get_json()
    states = states["states"]["items"]

    location_fips = []
    for state in states:
        location_fips.append(state["fips_code"])

    client.post(
        url + f"/{scholarship_id}/states",
        json={"location_fips": location_fips})

    response = client.get(url + f"/{scholarship_id}/states")
    states = response.get_json()
    states = states["states"]["items"]

    for i, state in enumerate(states):
        assert state["fips_code"] == location_fips[i]

    # delete scholarship states

    client.delete(
        url + f"/{scholarship_id}/states",
        json={"location_fips": [location_fips[0], location_fips[3]]})

    del location_fips[0]
    del location_fips[2]

    response = client.get(url + f"/{scholarship_id}/states")
    states = response.get_json()
    states = states["states"]["items"]

    for i, state in enumerate(states):
        assert state["fips_code"] == location_fips[i]


def test_scholarship_counties(app, client, auth):
    """ add, get and delete scholarship counties """

    with app.app_context():
        _save_states(1)

        scholarship = Scholarship(name="test scholarship")
        db.session.add(scholarship)
        db.session.commit()
        scholarship_id = scholarship.public_id

    auth.login()

    response = client.get("/api/locations/counties")

    counties = response.get_json()
    counties = counties["counties"]["items"]

    location_fips = []
    for county in counties:
        location_fips.append(county["fips_code"])

    client.post(
        url + f"/{scholarship_id}/counties",
        json={"location_fips": location_fips})

    response = client.get(url + f"/{scholarship_id}/counties")
    counties = response.get_json()
    counties = counties["counties"]["items"]

    for i, county in enumerate(counties):
        assert county["fips_code"] == location_fips[i]

    # delete scholarship counties

    client.delete(
        url + f"/{scholarship_id}/counties",
        json={"location_fips": [location_fips[0], location_fips[3]]})

    del location_fips[0]
    del location_fips[2]

    response = client.get(url + f"/{scholarship_id}/counties")
    counties = response.get_json()
    counties = counties["counties"]["items"]

    for i, county in enumerate(counties):
        assert county["fips_code"] == location_fips[i]


def test_scholarship_places(app, client, auth):
    """ add, get and delete scholarship places """

    with app.app_context():
        _save_states(1)

        scholarship = Scholarship(name="test scholarship")
        db.session.add(scholarship)
        db.session.commit()
        scholarship_id = scholarship.public_id

    auth.login()

    response = client.get("/api/locations/places")

    places = response.get_json()
    places = places["places"]["items"]

    location_fips = []
    for place in places:
        location_fips.append(place["fips_code"])

    client.post(
        url + f"/{scholarship_id}/places",
        json={"location_fips": location_fips})

    response = client.get(url + f"/{scholarship_id}/places")
    places = response.get_json()
    places = places["places"]["items"]

    for i, place in enumerate(places):
        assert place["fips_code"] == location_fips[i]

    # delete scholarship places

    client.delete(
        url + f"/{scholarship_id}/places",
        json={"location_fips": [location_fips[0], location_fips[3]]})

    del location_fips[0]
    del location_fips[2]

    response = client.get(url + f"/{scholarship_id}/places")
    places = response.get_json()
    places = places["places"]["items"]

    for i, place in enumerate(places):
        assert place["fips_code"] == location_fips[i]


def test_scholarship_consolidated_cities(app, client, auth):
    """ add, get and delete scholarship consolidated_cities """

    with app.app_context():
        _save_states(14)

        scholarship = Scholarship(name="test scholarship")
        db.session.add(scholarship)
        db.session.commit()
        scholarship_id = scholarship.public_id

    auth.login()

    response = client.get("/api/locations/consolidated_cities")

    consolidated_cities = response.get_json()
    consolidated_cities = consolidated_cities["consolidated_cities"]["items"]

    location_fips = []
    for consolidated_city in consolidated_cities:
        location_fips.append(consolidated_city["fips_code"])

    client.post(
        url + f"/{scholarship_id}/consolidated_cities",
        json={"location_fips": location_fips})

    response = client.get(url + f"/{scholarship_id}/consolidated_cities")
    consolidated_cities = response.get_json()
    consolidated_cities = consolidated_cities["consolidated_cities"]["items"]

    for i, consolidated_city in enumerate(consolidated_cities):
        assert consolidated_city["fips_code"] == location_fips[i]

    # delete scholarship consolidated_cities

    client.delete(
        url + f"/{scholarship_id}/consolidated_cities",
        json={"location_fips": [location_fips[0], location_fips[2]]})

    del location_fips[0]
    del location_fips[1]

    response = client.get(url + f"/{scholarship_id}/consolidated_cities")
    consolidated_cities = response.get_json()
    consolidated_cities = consolidated_cities["consolidated_cities"]["items"]

    for i, consolidated_city in enumerate(consolidated_cities):
        assert consolidated_city["fips_code"] == location_fips[i]
