from app.models.detail import Detail
from app.models.college import College
from app.models.college_details import CollegeDetails
from app import db

url = "/api/details"


def test_get_details(app, client, auth):
    """ test get details """

    auth.login()

    types = ["integer", "decimal", "string", "boolean"]
    values = ["100", "3.1415", "test example", "true"]
    with app.app_context():
        for i in range(50):
            index = i % len(types)
            detail = Detail(
                name=f"detail {i}", type=types[index], value=values[index])

            db.session.add(detail)
        db.session.commit()

        response = client.get(url)

        # get colleges

        response = client.get(url)
        data = response.get_json()
        details = data["items"]

        for i, detail in enumerate(details):
            detail_model = Detail.get(detail["id"])
            assert detail == detail_model.for_pagination()

        # get detail that ends with "ge 2"

        search = "il 2"
        response = client.get(url + f"?search={search}")
        data = response.get_json()
        details = data["items"]

        assert len(details) > 0

        for detail in details:
            assert detail["name"].find(search) != -1


def test_get_detail(app, client, auth):
    """ test gets single detail """

    auth.login()

    with app.app_context():
        detail_properties = {
            "name": "test detail",
            "type": "string",
            "value": "test value"
        }
        detail = Detail(**detail_properties)
        db.session.add(detail)
        db.session.commit()

        response = client.get(url + f"/{detail.id}")
        detail_response = response.get_json()

        assert detail_response == {"name"}


def test_patch_detail(app, client, auth):
    """ test posts single detail """

    auth.login()

    with app.app_context():
        detail = Detail(name="test detail", type="string", value="test value")
        db.session.add(detail)
        db.session.commit()

        detail_properties = {"type": "integer", "value": "1.2"}

        # errors

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 400

        detail_properties["value"] = "some string"

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 400

        # success

        detail_properties["value"] = "1"

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 200

        detail_url = response.get_json()["detail"]

        response = client.get(detail_url)

        detail_response = response.get_json()

        assert detail_response == dict(
            id=detail.id, name=detail.name, **detail_properties)

        detail_properties = {"type": "decimal", "value": "test"}

        # errors

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 400

        # success

        detail_properties["value"] = "1.3"

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 200

        detail_url = response.get_json()["detail"]

        response = client.get(detail_url)

        detail_response = response.get_json()

        assert detail_response == dict(
            id=detail.id, name=detail.name, **detail_properties)

        detail_properties = {"type": "boolean", "value": "3"}

        # errors

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 400

        detail_properties["value"] = "some string"

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 400

        # success

        detail_properties["value"] = "1"

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 200

        detail_url = response.get_json()["detail"]

        response = client.get(detail_url)

        detail_response = response.get_json()

        assert detail_response == dict(
            id=detail.id, name=detail.name, **detail_properties)

        detail_properties = {"type": "string", "value": 3}

        # errors

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 400

        # success

        detail_properties["value"] = "test example"

        response = client.patch(url + f"/{detail.id}", json=detail_properties)
        assert response.status_code == 200

        detail_url = response.get_json()["detail"]

        response = client.get(detail_url)

        detail_response = response.get_json()

        assert detail_response == dict(
            id=detail.id, name=detail.name, **detail_properties)


def test_detail_college(app, client, auth):
    """tests detail college"""
    auth.login()

    with app.test_request_context():
        detail = Detail(name="test detail")
        db.session.add(detail)

        college_details = CollegeDetails(name=f"test college 1")
        college = College(college_details=college_details)
        db.session.add(college_details)
        db.session.add(college)

        college.add_additional_detail(detail)

        db.session.commit()

        response = client.get(url + f"/{detail.id}/college")
        detail_colleges = response.get_json()

        college = College.query.first()
        assert detail_colleges == college.to_dict()