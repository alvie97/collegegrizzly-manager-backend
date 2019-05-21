import flask
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