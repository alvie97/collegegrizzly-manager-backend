from app import db
from app.models.scholarship import Scholarship
from app.models.scholarship_details import ScholarshipDetails

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

    auth.login()

    # create scholarship

    data = {
        "name": "test post scholarship",
        "amount": "test scholarship amount"
    }

    response = client.post(url, json=data)
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
