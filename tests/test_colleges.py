from decimal import Decimal
import flask

from app import db
from app.utils import generate_public_id
from app.models.college import College
from app.models import college_details as college_details_model

url = "/api/colleges"


def test_get_colleges(app, client, auth):
    """ get all colleges and test search function """

    # create colleges to test

    colleges_properties = []

    with app.app_context():
        for i in range(50):

            colleges_properties.append({"name": f"test college {i}"})

            college_details = college_details_model.CollegeDetails(
                **colleges_properties[i])
            college = College(college_details=college_details)
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


def test_create_college(app, client, auth):
    """creates college"""

    auth.login()

    # create college

    data = {"name": "test post college"}

    response = client.post(url, json=data)
    response_data = response.get_json()
    college_url = response_data["college"]

    response = client.get(college_url)
    response_data = response.get_json()

    with app.app_context():
        college = College.get(response_data["id"])

        assert college is not None
        assert college.to_dict() == response_data


def test_patch_college(app, client, auth):
    # update college

    auth.login()

    patch_data = {"name": "test patch college", "in_state_tuition": 1200}

    with app.app_context():
        college_details = college_details_model.CollegeDetails(**patch_data)
        college = College(college_details=college_details)
        db.session.add(college)
        db.session.commit()
        college_id = college.id

        response = client.patch(url + f"/{college_id}", json=patch_data)

    response_data = response.get_json()
    college_url = response_data["college"]

    response = client.get(college_url)
    response_data = response.get_json()

    with app.app_context():
        college = College.get(response_data["id"])

        assert college is not None
        assert college.to_dict() == response_data


def test_delete_college(app, client, auth):
    """ create colleges and edit them"""

    # delete college
    auth.login()

    with app.app_context():
        college_details = college_details_model.CollegeDetails()
        college = College(college_details=college_details)
        db.session.add(college)
        db.session.commit()
        college_id = college.id
        college_details_id = college_details.id

    client.delete(url + f"/{college_id}")

    with app.app_context():
        college_details = college_details_model.CollegeDetails.get(
            college_details_id)
        college = College.get(college_id)

        assert college is None and college_details is None