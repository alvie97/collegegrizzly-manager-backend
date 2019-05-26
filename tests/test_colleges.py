from app import db
from app.models.college import College
from app.models.college_details import CollegeDetails
from app.models.detail import Detail
from app.models.major import Major
from app.models.scholarship import Scholarship

url = "/api/colleges"


def test_get_colleges(app, client, auth):
    """ get all colleges and test search function """

    # create colleges to test

    colleges_properties = []

    with app.app_context():
        for i in range(50):

            colleges_properties.append({"name": f"test college {i}"})

            college_details = CollegeDetails(**colleges_properties[i])
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

    assert len(colleges) > 0

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

    with app.test_request_context():
        college = College.get(response_data["id"])

        assert college is not None
        assert college.to_dict() == response_data


def test_patch_college(app, client, auth):
    # update college

    auth.login()

    patch_data = {"name": "test patch college", "in_state_tuition": 1200}

    with app.app_context():
        college_details = CollegeDetails(**patch_data)
        college = College(college_details=college_details)
        db.session.add(college)
        db.session.commit()
        college_id = college.id

        response = client.patch(url + f"/{college_id}", json=patch_data)

    response_data = response.get_json()
    college_url = response_data["college"]

    response = client.get(college_url)
    response_data = response.get_json()

    with app.test_request_context():
        college = College.get(response_data["id"])

        assert college is not None
        assert college.to_dict() == response_data


def test_delete_college(app, client, auth):
    """ create colleges and edit them"""

    # delete college
    auth.login()

    with app.app_context():
        college_details = CollegeDetails()
        college = College(college_details=college_details)
        db.session.add(college)
        db.session.commit()
        college_id = college.id
        college_details_id = college_details.id

    client.delete(url + f"/{college_id}")

    with app.app_context():
        college_details = CollegeDetails.get(college_details_id)
        college = College.get(college_id)

        assert college is None and college_details is None


def test_college_majors(app, client, auth):
    """ tests add, read and remove majors """
    auth.login()

    with app.app_context():
        college_details = CollegeDetails(name="test college")
        college = College(college_details=college_details)
        db.session.add(college_details)
        db.session.add(college)

        for i in range(5):
            db.session.add(Major(name=f"test major {i}"))

        db.session.commit()

        response = client.post(
            url + f"/{college.id}/majors", json=[x for x in range(5)])

        majors_url = response.get_json()["majors"]

        response = client.get(majors_url)

        majors = response.get_json()["items"]

        for major in majors:
            major_record = Major.get(major["id"])

            assert major_record is not None

        response = client.delete(
            url + f"/{college.id}/majors", json=[x for x in range(3)])

        majors_url = response.get_json()["majors"]

        response = client.get(majors_url)

        majors = response.get_json()["items"]

        for major in majors:
            assert major["id"] in [3, 4]


def test_college_additional_details(app, client, auth):
    """tests college additional details"""

    auth.login()

    with app.test_request_context():
        college_details = CollegeDetails(name="test college")
        college = College(college_details=college_details)

        db.session.add(college_details)
        db.session.add(college)
        db.session.commit()

        detail = {"name": "test detail", "type": "integer", "value": "3"}

        response = client.post(
            url + f"/{college.id}/additional_details", json=detail)

        additional_details_url = response.get_json()["additional_details"]

        response = client.get(additional_details_url)
        additional_details = response.get_json()

        detail = Detail.query.first()

        assert additional_details[0] == detail.to_dict()

        response = client.delete(
            url + f"/{college.id}/additional_details/{detail.id}")

        additional_details_url = response.get_json()["additional_details"]

        response = client.get(additional_details_url)
        additional_details = response.get_json()

        assert len(additional_details) == 0


def test_get_college_scholarships(app, client, auth, scholarships, colleges):
    """
    Tests get_scholarships endpoint
    """

    with app.app_context():
        college = College.query.first()
        scholarships = Scholarship.query.limit(5)

        for scholarship in scholarships:
            college.scholarships.append(scholarship)

        assert college.scholarships.count() == 5

    auth.login()

    response = client.get(url + "/1/scholarships")

    assert response.status_code == 200

    scholarships = response.get_json()["items"]

    assert len(scholarship) > 0

    with app.app_context():
        college = College.query.first()

        for scholarship in scholarships:
            assert college.scholarships.filter_by(
                id=scholarship["id"], name=scholarship["name"]).count() == 1
