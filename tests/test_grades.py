from app import db
from app.models.grade import Grade

url = "/api/grades"


def test_get_grades(app, client, auth):
    """ get all grades and test search function """

    # create grades to test

    grades_properties = []

    with app.app_context():
        for i in range(50):

            grades_properties.append({
                "name": f"test grade {i}",
                "max": 132,
                "min": 100
            })

            grade = Grade(**grades_properties[i])
            db.session.add(grade)

        db.session.commit()

    # login

    auth.login()

    # get grades

    response = client.get(url)
    data = response.get_json()
    grades = data["items"]

    for i, grade in enumerate(grades):
        assert grade["name"] == grades_properties[i]["name"]

    # get grade that ends with "de 2"

    response = client.get(url + "?search=de 2")
    data = response.get_json()
    grades = data["items"]

    assert len(grades) > 0

    for grade in grades:
        assert grade["name"].find("de 2") != -1


def test_create_grade(app, client, auth):
    """creates grade"""

    auth.login()

    # create grade

    data = {"name": "test post grade", "max": 132, "min": 140}

    response = client.post(url, json=data)
    assert response.status_code == 400

    data["min"] = 100

    response = client.post(url, json=data)
    response_data = response.get_json()
    grade_url = response_data["grade"]

    response = client.get(grade_url)
    response_data = response.get_json()

    with app.app_context():
        grade = Grade.get(response_data["id"])

        assert grade is not None
        assert grade.to_dict() == response_data


def test_patch_grade(app, client, auth):
    # update grade

    auth.login()

    patch_data = {"name": "test post grade", "max": 132, "min": 122}

    with app.app_context():
        grade = Grade(name="test grade", max=142, min=100)
        db.session.add(grade)
        db.session.commit()
        grade_id = grade.id

        response = client.patch(url + f"/{grade_id}", json=patch_data)

    response_data = response.get_json()
    grade_url = response_data["grade"]

    response = client.get(grade_url)
    response_data = response.get_json()

    with app.test_request_context():
        grade = Grade.get(response_data["id"])

        assert grade is not None
        assert grade.to_dict() == response_data


def test_delete_grade(app, client, auth):
    """ create grades and edit them"""

    # delete grade
    auth.login()

    with app.app_context():
        grade = Grade(name="test grade")
        db.session.add(grade)
        db.session.commit()

        client.delete(url + f"/{grade.id}")

        grade = Grade.get(grade.id)

        assert grade is None
