from app.models import college as college_model


def test_add_lr_to_college_success_0(app, client, auth, colleges):
    """
    Adds location requirement with Adress place, county, state and blacklist.

    expected output:
        Successfully adds address to the Database.
    """

    json = {
        "state": "test state",
        "county": "test county",
        "place": "test place",
        "zip_code": None,
        "blacklist": 1
    }

    auth.login()

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 201

    with app.app_context():
        college = college_model.College.query.first()

        assert college.location_requirements.count() == 1

        location = college.location_requirements.first()

        assert location.state == json["state"]
        assert location.county == json["county"]
        assert location.place == json["place"]
        assert location.blacklist == True


def test_add_lr_to_college_success_1(app, client, auth, colleges):
    """
    Adds location requirement with Adress county, state and blacklist.

    expected output:
        Successfully adds address to the Database.
    """
    json = {
        "state": "test state",
        "county": "test county",
        "place": None,
        "zip_code": None,
        "blacklist": 1
    }

    auth.login()

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 201

    with app.app_context():
        college = college_model.College.query.first()

        assert college.location_requirements.count() == 1

        location = college.location_requirements.first()

        assert location.state == json["state"]
        assert location.county == json["county"]
        assert location.blacklist == True


def test_add_lr_to_college_success_2(app, client, auth, colleges):
    """
    Adds location requirement with Adress state and blacklist.

    expected output:
        Successfully adds address to the Database.
    """
    json = {
        "state": "test state",
        "county": None,
        "place": None,
        "zip_code": None,
        "blacklist": 1
    }

    auth.login()

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 201

    with app.app_context():
        college = college_model.College.query.first()

        assert college.location_requirements.count() == 1

        location = college.location_requirements.first()

        assert location.state == json["state"]
        assert location.blacklist == True


def test_add_lr_to_college_success_3(app, client, auth, colleges):
    """
    Adds location requirement with Adress zip_code and blacklist.

    expected output:
        Successfully adds zip_code to the Database.
    """
    json = {
        "state": "test state",
        "county": None,
        "place": None,
        "zip_code": "12345",
        "blacklist": 1
    }

    auth.login()

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 201

    with app.app_context():
        college = college_model.College.query.first()

        assert college.location_requirements.count() == 1

        location = college.location_requirements.first()

        assert location.zip_code == json["zip_code"]
        assert location.blacklist == True

    json = {
        "state": "test state",
        "county": None,
        "place": None,
        "zip_code": "12345-1234",
        "blacklist": 1
    }

    auth.login()

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 201

    with app.app_context():
        college = college_model.College.query.first()

        assert college.location_requirements.count() == 2

        location = college.location_requirements.filter_by(id=2).first()

        assert location.zip_code == json["zip_code"]
        assert location.blacklist == True


def test_add_lr_to_college_success_4(app, client, auth, colleges):
    """
    Adds location requirement with Adress zip_code and blacklist.

    expected output:
        Successfully adds only zip_code omitting address to the Database.
    """
    pass

    json = {
        "state": "test state",
        "county": "test county",
        "place": "test place",
        "zip_code": "12345",
        "blacklist": 1
    }

    auth.login()

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 201

    with app.app_context():
        college = college_model.College.query.first()

        assert college.location_requirements.count() == 1

        location = college.location_requirements.first()

        assert location.state == None
        assert location.county == None
        assert location.place == None
        assert location.zip_code == json["zip_code"]
        assert location.blacklist == True


def test_add_lr_to_college_failure_0(app, client, auth, colleges):
    """No data provided or bad structure."""

    auth.login()

    response = client.post("api/colleges/1/location_requirements", json={})

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    response = client.post("api/colleges/1/location_requirements", json=[])

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"


def test_add_lr_to_college_failure_1(app, client, auth, colleges):
    """Missing fields."""

    auth.login()

    json = {"blacklist": 1}

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "missing fields"


def test_add_lr_to_college_failure_2(app, client, auth, colleges):
    """Place defined but either county or state is not."""

    auth.login()

    json = {
        "state": None,
        "county": "test county",
        "place": "test place",
        "zip_code": None,
        "blacklist": 1
    }

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "if place is defined, county and state must be defined"


def test_add_lr_to_college_failure_3(app, client, auth, colleges):
    """county defined but state is not."""

    auth.login()

    json = {
        "state": None,
        "county": "test county",
        "place": None,
        "zip_code": None,
        "blacklist": 1
    }

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "if county is defined, state must be defined"


def test_add_lr_to_college_failure_4(app, client, auth, colleges):
    """nor zip_code or any of the address properties are defined."""

    auth.login()

    json = {
        "state": None,
        "county": None,
        "place": None,
        "zip_code": None,
        "blacklist": 1
    }

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "zip code or state must be defined"


def test_add_lr_to_college_failure_5(app, client, auth, colleges):
    """blacklist is not either 1 or 0."""

    auth.login()

    json = {
        "state": None,
        "county": None,
        "place": None,
        "zip_code": "12345",
        "blacklist": "True"
    }

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "blacklist must be either 1 or 0"


def test_add_lr_to_college_failure_6(app, client, auth, colleges):
    """zip code is not valid"""

    auth.login()

    json = {
        "state": None,
        "county": None,
        "place": None,
        "zip_code": "123456",
        "blacklist": 1
    }

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid zip code"

    json = {
        "state": None,
        "county": None,
        "place": None,
        "zip_code": "12345-123",
        "blacklist": 1
    }

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid zip code"

    json = {
        "state": None,
        "county": None,
        "place": None,
        "zip_code": "12345-12345",
        "blacklist": 1
    }

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid zip code"

    json = {
        "state": None,
        "county": None,
        "place": None,
        "zip_code": "123-123",
        "blacklist": 1
    }

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid zip code"

    json = {
        "state": None,
        "county": None,
        "place": None,
        "zip_code": "asfjalskwer",
        "blacklist": 1
    }

    response = client.post("api/colleges/1/location_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid zip code"
