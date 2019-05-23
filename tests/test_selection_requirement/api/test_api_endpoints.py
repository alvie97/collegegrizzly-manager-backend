import flask
import app as application
from app.models import question as question_model
from app.models import scholarship as scholarship_model

url = "/api/scholarships"


def test_add_selection_requirement_to_scholarship_success(
        app, client, auth, scholarships, questions):
    """
    Adds selecetion requirement to scholarship successfully.
    """

    auth.login()

    json = {"question_id": 1, "description": "test description"}

    response = client.post(url + "/1/selection_requirements", json=json)

    assert response.status_code == 200

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()

        assert scholarship.selection_requirements.count() == 1
        assert scholarship.has_selection_requirement(1)

        selection_requirement = scholarship.selection_requirements.first()

        assert json["question_id"] == selection_requirement.question.id
        assert json["description"] == selection_requirement.description

    with app.test_request_context():
        response_json = response.get_json()
        assert response_json["selection_requirements"] == flask.url_for(
            "scholarships.get_selection_requirements", id=1)


def test_add_selection_requirement_to_scholarship_failure(
        app, client, auth, questions, scholarships):
    """
    Failure cases for adding a selection requirement to a scholarship
    """
    auth.login()

    json = ["test"]

    response = client.post(url + "/1/selection_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    json = {}

    response = client.post(url + "/1/selection_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    json = {"question_id": 1}

    response = client.post(url + "/1/selection_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "missing fields"

    json = {"description": "asdfasdf"}

    response = client.post(url + "/1/selection_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "missing fields"

    json = {"question_id": "asdf23"}

    response = client.post(url + "/1/selection_requirements", json=json)

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid id"

    json = {"question_id": 1, "description": None}

    response = client.post(url + "/9999/selection_requirements", json=json)

    assert response.status_code == 404

    json = {"question_id": 999999, "description": None}

    response = client.post(url + "/1/selection_requirements", json=json)

    assert response.status_code == 404

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()

        assert scholarship.selection_requirements.count() == 0


def test_delete_selection_requirement_from_scholarship_success(
        app, client, auth, questions, scholarships):
    """
    Tests delete selection requirement from scholarship success
    """
    auth.login()
    with app.test_request_context():
        scholarship = scholarship_model.Scholarship.query.first()
        question = question_model.Question.query.first()

        scholarship.add_selection_requirement(question)

        application.db.session.commit()

        assert scholarship.selection_requirements.count() == 1

        response = client.delete(url + "/1/selection_requirements/1")
        assert response.status_code == 200
        assert scholarship.selection_requirements.count() == 0

        assert response.get_json()["selection_requirements"] == flask.url_for(
            "scholarships.get_selection_requirements", id=1)


def test_delete_selection_requirement_from_scholarship_failure(
        app, client, auth, questions, scholarships):
    """
    Tests delete selection requirement from scholarship failure
    """
    auth.login()
    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        question = question_model.Question.query.first()

        scholarship.add_selection_requirement(question)

        application.db.session.commit()

        response = client.delete(url + "/999/selection_requirements/1")
        assert response.status_code == 404

        response = client.delete(url + "/1/selection_requirements/999")
        assert response.status_code == 404
        assert response.get_json(
        )["message"] == "scholarship doesn't have selection requirement with question"

        assert scholarship.selection_requirements.count() == 1


def test_get_selection_requirements_from_scholarship_success(
        app, client, auth, questions, scholarships):
    """
    Tests get selection requirement from scholarship success
    """
    auth.login()
    with app.test_request_context():
        scholarship = scholarship_model.Scholarship.query.first()
        question = question_model.Question.query.first()

        scholarship.add_selection_requirement(question)

        application.db.session.commit()

        response = client.get(url + "/1/selection_requirements")
        selection_requirement = scholarship.selection_requirements.first()
        assert response.status_code == 200
        assert response.get_json() == [selection_requirement.to_dict()]


def test_get_selection_requirements_from_scholarship_failure(
        app, client, auth, questions, scholarships):
    """
    Tests get selection requirement from scholarship failure
    """
    auth.login()
    response = client.get(url + "/9999/selection_requirements")
    assert response.status_code == 404


def test_add_option_to_selection_requirement_succes(
        app, client, auth, scholarships, questions, options):
    """
    Tests add option to selection requirement, success cases
    """
    auth.login()

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        question = question_model.Question.query.first()

        scholarship.add_selection_requirement(question)
        application.db.session.commit()

        json = [1, 2, 3]

    response = client.post(
        url + "/1/selection_requirements/1/options", json=json)

    assert response.status_code == 200

    with app.app_context():

        scholarship = scholarship_model.Scholarship.query.first()
        selection_requirement = scholarship.selection_requirements.first()
        options_array = selection_requirement.options.all()

        for index, option in enumerate(options_array):
            assert option.id == json[index]