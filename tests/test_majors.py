from decimal import Decimal
import flask
import sqlalchemy

from app import db
from app.models.major import Major
from app.models.college import College
from app.models.college_details import CollegeDetails

url = "/api/majors"


def test_get_majors(app, client, auth):
    """ get all majors and test search function """

    # create majors to test

    majors_properties = []

    with app.app_context():
        for i in range(50):

            majors_properties.append({"name": f"test major {i}"})

            major = Major(**majors_properties[i])
            db.session.add(major)

        db.session.commit()

    # login

    auth.login()

    # get majors

    response = client.get(url)
    data = response.get_json()
    majors = data["items"]

    for i, major in enumerate(majors):
        assert major["name"] == majors_properties[i]["name"]

    # get major that ends with "or 2"

    response = client.get(url + "?search=or 2")
    data = response.get_json()
    majors = data["items"]

    assert len(majors) > 0

    for major in majors:
        assert major["name"].find("or 2") != -1


def test_create_major(app, client, auth):
    """creates major"""

    auth.login()

    # create major

    data = {"name": "test post major"}

    response = client.post(url, json=data)
    response_data = response.get_json()
    major_url = response_data["major"]

    response = client.get(major_url)
    response_data = response.get_json()

    with app.test_request_context():
        major = Major.get(response_data["id"])

        assert major is not None
        assert major.to_dict() == response_data


def test_delete_major(app, client, auth):
    """ create majors and edit them"""

    # delete major
    auth.login()

    with app.app_context():
        major = Major(name="test major")
        db.session.add(major)
        db.session.commit()

        client.delete(url + f"/{major.id}")

        major = Major.get(major.id)

        assert major is None


def test_majors_colleges(app, client, auth):
    auth.login()

    with app.app_context():
        major = Major(name="test major")
        db.session.add(major)

        for i in range(10):

            college_details = CollegeDetails(name=f"test college {i}")
            college = College(college_details=college_details)
            db.session.add(college_details)
            db.session.add(college)

            college.add_major(major)

        db.session.commit()

        response = client.get(url + f"/{major.id}/colleges")
        major_colleges = response.get_json()

        major_colleges = major_colleges["items"]

        colleges = College.query.limit(5).all()

        for i, college in enumerate(colleges):
            assert major_colleges[i]["name"] == college.college_details.name