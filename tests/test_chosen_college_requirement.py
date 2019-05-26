import app as application
from app.models import scholarship as scholarship_model
from app.models import question as question_model


def test_chosen_college_requirement_scholarship_schema(app):
    """Test chosen college requirement for scholarship, database schema.

    * check college many to many relationship with questions.
    """

    with app.app_context():
        scholarship = scholarship_model.Scholarship()
        application.db.session.add(scholarship)

        for i in range(10):
            question = question_model.Question(name=f"question {i}")
            application.db.session.add(question)
            if i < 9:
                scholarship.add_chosen_college_requirement(question)

        application.db.session.commit()

        questions = question_model.Question.get_all()

        for question in questions:
            assert scholarship.has_chosen_college_requirement(question) == (
                not question.name == "question 9")

        for question in questions:
            scholarship.remove_chosen_college_requirement(question)

        assert scholarship.chosen_college_requirement.count() == 0


def test_add_chosen_college_requirement_scholarship_failure_0(
        app, client, auth):
    """json data is empty"""
    auth.login()
    url = "/api/scholarships/1/chosen_college_requirement"
    json = []
    response = client.post(url, json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"


def test_add_chosen_college_requirement_scholarship_failure_1(
        app, client, auth):
    """json is not a list"""
    auth.login()
    url = "/api/scholarships/1/chosen_college_requirement"
    json = "not a list"
    response = client.post(url, json=json)
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"


def test_add_chosen_college_requirement_scholarship_failure_2(
        app, client, auth, scholarships):
    """scholarship is not found"""
    auth.login()

    json = [1, 3]
    url = "/api/scholarships/9999999999/chosen_college_requirement"
    response = client.post(url, json=json)

    assert response.status_code == 404
    assert response.get_json()["message"] == "resource not found"


def test_add_chosen_college_requirement_scholarship_failure_3(
        app, client, auth, questions, scholarships):
    """question's id is not valid"""

    auth.login()

    json = ["test"]
    url = "/api/scholarships/1/chosen_college_requirement"

    response = client.post(url, json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid id"


def test_add_chosen_college_requirement_scholarship_failure_4(
        app, client, auth, scholarships):
    """question's id is not valid"""

    auth.login()

    json = ["test"]
    url = "/api/scholarships/1/chosen_college_requirement"

    response = client.post(url, json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid id"


def test_add_chosen_college_requirement_scholarship_failure_5(
        app, client, auth, scholarships, questions):
    """question not found"""

    auth.login()

    json = [1, 999999999]
    url = "/api/scholarships/1/chosen_college_requirement"

    response = client.post(url, json=json)

    assert response.status_code == 404
    assert response.get_json()["message"] == "resource not found"

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        assert scholarship.chosen_college_requirement.count() == 0


def test_add_chosen_college_requirement_scholarship_success_0(
        app, client, auth, scholarships, questions):
    """adds chosen college requirement questions to scholarship"""

    auth.login()

    json = [1, 2, 3]
    url = "/api/scholarships/1/chosen_college_requirement"

    response = client.post(url, json=json)

    assert response.get_json(
    )["message"] == "added questions to chosen college requirement"

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        assert scholarship.chosen_college_requirement.count() == 3

        for id in json:
            assert scholarship.chosen_college_requirement.filter_by(
                id=id).count() == 1


def test_remove_chosen_college_requirement_scholarship_failure_0(
        app, client, auth):
    """json data is empty"""
    auth.login()
    url = "/api/scholarships/1/chosen_college_requirement"
    json = []
    response = client.delete(url, json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"


def test_remove_chosen_college_requirement_scholarship_failure_1(
        app, client, auth):
    """json is not a list"""
    auth.login()
    url = "/api/scholarships/1/chosen_college_requirement"
    json = "not a list"
    response = client.delete(url, json=json)
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"


def test_remove_chosen_college_requirement_scholarship_failure_2(
        app, client, auth, scholarships):
    """scholarship is not found"""
    auth.login()

    json = [1, 3]
    url = "/api/scholarships/9999999999/chosen_college_requirement"
    response = client.delete(url, json=json)

    assert response.status_code == 404
    assert response.get_json()["message"] == "resource not found"


def test_remove_chosen_college_requirement_scholarship_failure_3(
        app, client, auth, questions, scholarships):
    """question's id is not valid"""

    auth.login()

    json = ["test"]
    url = "/api/scholarships/1/chosen_college_requirement"

    response = client.delete(url, json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid id"


def test_remove_chosen_college_requirement_scholarship_failure_4(
        app, client, auth, scholarships):
    """question's id is not valid"""

    auth.login()

    json = ["test"]
    url = "/api/scholarships/1/chosen_college_requirement"

    response = client.delete(url, json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid id"


def test_remove_chosen_college_requirement_scholarship_failure_5(
        app, client, auth, scholarships, questions):
    """question not found"""

    auth.login()

    json = [1, 999999999]
    url = "/api/scholarships/1/chosen_college_requirement"

    response = client.delete(url, json=json)

    assert response.status_code == 404
    assert response.get_json()["message"] == "resource not found"

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        assert scholarship.chosen_college_requirement.count() == 0


def test_remove_chosen_college_requirement_scholarship_success_0(
        app, client, auth, scholarships, questions):
    """removes chosen college requirement questions to scholarship"""

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        questions_for_scholarship = question_model.Question.query.filter(
            question_model.Question.id.in_((1, 2, 3, 4))).all()

        scholarship.chosen_college_requirement = questions_for_scholarship
        application.db.session.commit()

    auth.login()

    json = [1, 2, 3]
    url = "/api/scholarships/1/chosen_college_requirement"

    response = client.delete(url, json=json)

    assert response.get_json(
    )["message"] == "removed questions to chosen college requirement"

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        assert scholarship.chosen_college_requirement.count() == 1
        requirement = scholarship.chosen_college_requirement.first()
        assert requirement.id == 4


def test_get_scholarship_chosen_college_requirement(app, client, auth,
                                                    scholarships, questions):
    """tests GET method for scholarship's chosen college requirement"""
    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        questions_for_scholarship = question_model.Question.query.filter(
            question_model.Question.id.in_((1, 2, 3, 4))).all()

        scholarship.chosen_college_requirement = questions_for_scholarship
        application.db.session.commit()

    auth.login()

    url = "/api/scholarships/1/chosen_college_requirement"
    response = client.get(url)

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0

    with app.test_request_context():
        for question_requirement in data:
            question = question_model.Question.first(
                id=question_requirement["id"])
            assert question.to_dict() == question_requirement
