from app import db
from app.models.scholarship import Scholarship
from app.models.scholarship_details import ScholarshipDetails
from app.models.detail import Detail
from app.models.college import College
from app.models.college_details import CollegeDetails

url = "/api/scholarships"


def test_get_scholarships(app, client, auth):
    """ get all scholarships and test search function """

    # create scholarships to test

    scholarships_properties = []

    with app.app_context():
        for i in range(50):

            scholarships_properties.append({"name": f"test scholarship {i}"})

            scholarship_details = ScholarshipDetails(
                **scholarships_properties[i])
            scholarship = Scholarship(scholarship_details=scholarship_details)
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

    search = "ip 2"
    response = client.get(url + f"?search={search}")
    data = response.get_json()
    scholarships = data["items"]

    assert len(scholarships) > 0

    for scholarship in scholarships:
        assert scholarship["name"].find(search) != -1


def test_create_scholarship(app, client, auth):
    """creates scholarship"""

    with app.app_context():
        college_details = CollegeDetails(name="test college")
        college = College(college_details=college_details)
        db.session.add(college_details)
        db.session.add(college)
        db.session.commit()
        college_id = college.id

    auth.login()

    # create scholarship

    data = {
        "name": "test post scholarship",
        "amount": "test scholarship amount"
    }

    response = client.post(url + f"?college_id={college_id}", json=data)
    response_data = response.get_json()
    scholarship_url = response_data["scholarship"]

    response = client.get(scholarship_url)
    response_data = response.get_json()

    with app.test_request_context():
        scholarship = Scholarship.get(response_data["id"])

        assert scholarship is not None
        assert scholarship.to_dict() == response_data


def test_patch_scholarship(app, client, auth):
    # update scholarship

    auth.login()

    patch_data = {"name": "test patch scholarship", "application_needed": 1}

    with app.app_context():
        scholarship_details = ScholarshipDetails(**patch_data)
        scholarship = Scholarship(scholarship_details=scholarship_details)
        db.session.add(scholarship)
        db.session.commit()
        scholarship_id = scholarship.id

        response = client.patch(url + f"/{scholarship_id}", json=patch_data)

    response_data = response.get_json()
    scholarship_url = response_data["scholarship"]

    response = client.get(scholarship_url)
    response_data = response.get_json()

    with app.test_request_context():
        scholarship = Scholarship.get(response_data["id"])

        assert scholarship is not None
        assert scholarship.to_dict() == response_data


def test_delete_scholarship(app, client, auth):
    """ create scholarships and edit them"""

    # delete scholarship
    auth.login()

    with app.app_context():
        scholarship_details = ScholarshipDetails()
        scholarship = Scholarship(scholarship_details=scholarship_details)
        db.session.add(scholarship)
        db.session.commit()
        scholarship_id = scholarship.id
        scholarship_details_id = scholarship_details.id

    client.delete(url + f"/{scholarship_id}")

    with app.app_context():
        scholarship_details = ScholarshipDetails.get(scholarship_details_id)
        scholarship = Scholarship.get(scholarship_id)

        assert scholarship is None and scholarship_details is None


def test_scholarship_additional_details(app, client, auth):
    """tests scholarship additional details"""

    auth.login()

    with app.test_request_context():
        scholarship_details = ScholarshipDetails(name="test scholarship")
        scholarship = Scholarship(scholarship_details=scholarship_details)

        db.session.add(scholarship_details)
        db.session.add(scholarship)
        db.session.commit()

        detail = {"name": "test detail", "type": "integer", "value": "3"}

        response = client.post(
            url + f"/{scholarship.id}/additional_details", json=detail)

        additional_details_url = response.get_json()["additional_details"]

        response = client.get(additional_details_url)
        additional_details = response.get_json()

        detail = Detail.query.first()

        assert additional_details[0] == detail.to_dict()

        response = client.delete(
            url + f"/{scholarship.id}/additional_details/{detail.id}")

        additional_details_url = response.get_json()["additional_details"]

        response = client.get(additional_details_url)
        additional_details = response.get_json()

        assert len(additional_details) == 0


def test_scholarships_needed(app, client, auth):
    """ add and delete scholarships needed """

    with app.app_context():

        college_details = CollegeDetails(name="test college")
        college = College(college_details=college_details)
        db.session.add(college)

        scholarship_details_1 = ScholarshipDetails(name="test scholarship 1")
        scholarship_details_2 = ScholarshipDetails(name="test scholarship 2")

        scholarship_1 = Scholarship(
            scholarship_details=scholarship_details_1, college=college)
        scholarship_2 = Scholarship(
            scholarship_details=scholarship_details_2, college=college)
        db.session.add(scholarship_1)
        db.session.add(scholarship_2)
        db.session.commit()
        scholarship_id_1 = scholarship_1.id
        scholarship_id_2 = scholarship_2.id

    auth.login()

    client.post(
        url + f"/{scholarship_id_1}/scholarships_needed",
        json=[scholarship_id_1, scholarship_id_2])

    response = client.get(url + f"/{scholarship_id_1}/scholarships_needed")
    scholarships_needed = response.get_json()

    assert scholarships_needed["meta"]["total_items"] == 1
    assert scholarships_needed["items"][0]["id"] == scholarship_id_2

    client.delete(
        url + f"/{scholarship_id_1}/scholarships_needed",
        json=[scholarship_id_2])

    response = client.get(url + f"/{scholarship_id_1}/scholarships_needed")
    scholarships_needed = response.get_json()

    assert scholarships_needed["meta"]["total_items"] == 0
