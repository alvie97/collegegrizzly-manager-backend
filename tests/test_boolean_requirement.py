from app.models import scholarship as scholarship_model
from app.models import association_tables
from app.models import question as question_model
import app as application
import flask


def test_post_boolean_requirement_scholarships_failure(
        app, client, auth, scholarships, questions):
    """test post_boolean_requirement route from scholarships failure cases"""

    auth.login()

    response = client.post("/api/scholarships/1/boolean_requirement", json={})
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    response = client.post("/api/scholarships/1/boolean_requirement", json=[])
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    response = client.post(
        "/api/scholarships/1/boolean_requirement", json={"question_id": 1})
    assert response.status_code == 400
    assert response.get_json()["message"] == "no question_id or required_value"

    response = client.post(
        "/api/scholarships/1/boolean_requirement",
        json={"question_id": "asdfasf"})
    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid id"

    response = client.post(
        "/api/scholarships/1/boolean_requirement",
        json={
            "question_id": 1,
            "required_value": "yes"
        })
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "required_value must be either 1 or 0"

    response = client.post(
        "/api/scholarships/999999999/boolean_requirement",
        json={
            "question_id": 1,
            "required_value": 0
        })
    assert response.status_code == 404

    response = client.post(
        "/api/scholarships/1/boolean_requirement",
        json={
            "question_id": 999999,
            "required_value": 0
        })
    assert response.status_code == 404


def test_post_boolean_requirement_scholarships_success(
        app, client, auth, scholarships, questions):
    """tests adding boolean requirement to scholarship"""

    auth.login()

    with app.test_request_context():
        scholarship = scholarship_model.Scholarship.query.first()
        get_boolean_requirement_url = flask.url_for(
            "scholarships.get_boolean_requirement", id=scholarship.id)

        json = {"question_id": 1, "required_value": 0}

        response = client.post(
            f"/api/scholarships/{scholarship.id}/boolean_requirement",
            json=json)
        assert response.status_code == 200

        json = {"question_id": 2, "required_value": 1}

        response = client.post(
            f"/api/scholarships/{scholarship.id}/boolean_requirement",
            json=json)
        assert response.get_json(
        )["boolean_requirement"] == get_boolean_requirement_url

        scholarship = scholarship_model.Scholarship.query.first()

        assert scholarship.boolean_requirement.filter(
            association_tables.BooleanRequirement.question_id.in_(
                (1, 2))).distinct().count() == 2

        json = {"question_id": 2, "required_value": 1}

        response = client.post(
            f"/api/scholarships/{scholarship.id}/boolean_requirement",
            json=json)
        assert response.get_json(
        )["boolean_requirement"] == get_boolean_requirement_url

        scholarship = scholarship_model.Scholarship.query.first()

        assert scholarship.boolean_requirement.count() == 2


def test_delete_boolean_requirement_scholarships_failure(
        app, client, auth, scholarships, questions):
    """test delete_boolean_requirement route from scholarships failure cases"""
    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        questions = question_model.Question.query.filter(
            question_model.Question.id.in_((1, 2)))

        for question in questions:
            scholarship.add_boolean_requirement(question, 1)

        application.db.session.commit()

    auth.login()

    response = client.delete(
        "/api/scholarships/1/boolean_requirement", json=[])
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    response = client.delete(
        "/api/scholarships/1/boolean_requirement", json={})
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    response = client.delete(
        "/api/scholarships/999999999/boolean_requirement", json=[1])
    assert response.status_code == 404

    response = client.delete(
        "/api/scholarships/1/boolean_requirement", json=[1, "test"])

    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid id"

    response = client.delete(
        "/api/scholarships/1/boolean_requirement", json=[1, 9999])
    assert response.status_code == 404

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        assert scholarship.boolean_requirement.filter(
            association_tables.BooleanRequirement.id.in_(
                (1, 2))).distinct().count() == 2


def test_delete_boolean_requirement_scholarship_success(
        app, client, auth, scholarships, questions):
    """test delete_boolean_requirement route from scholarships success cases"""

    auth.login()

    with app.test_request_context():
        scholarship = scholarship_model.Scholarship.query.first()
        questions = question_model.Question.query.filter(
            question_model.Question.id.in_((1, 2)))

        for question in questions:
            scholarship.add_boolean_requirement(question, 1)

        application.db.session.commit()

        get_boolean_requirement_url = flask.url_for(
            "scholarships.get_boolean_requirement", id=scholarship.id)

        json = [1]

        response = client.delete(
            f"/api/scholarships/{scholarship.id}/boolean_requirement",
            json=json)
        assert response.status_code == 200
        assert response.get_json(
        )["boolean_requirement"] == get_boolean_requirement_url

        scholarship = scholarship_model.Scholarship.query.first()

        assert scholarship.boolean_requirement.count() == 1
        assert scholarship.boolean_requirement.filter(
            association_tables.BooleanRequirement.question_id ==
            2).count() == 1

        json = [1]

        response = client.delete(
            f"/api/scholarships/{scholarship.id}/boolean_requirement",
            json=json)
        assert response.status_code == 200
        assert response.get_json(
        )["boolean_requirement"] == get_boolean_requirement_url

        scholarship = scholarship_model.Scholarship.query.first()

        assert scholarship.boolean_requirement.count() == 1
        assert scholarship.boolean_requirement.filter(
            association_tables.BooleanRequirement.question_id ==
            2).count() == 1

def test_get_boolean_requirement_scholarship_success(app, client, auth,
                                                     scholarships, questions):
    """tests get_boolean_requirement route from scholarships failure cases"""

    auth.login()

    response = client.get("/api/scholarships/99999/boolean_requirement")
    assert response.status_code == 404

def test_get_boolean_requirement_scholarship_success(app, client, auth,
                                                     scholarships, questions):
    """tests get_boolean_requirement route from scholarships success cases"""

    auth.login()

    with app.test_request_context():
        scholarship = scholarship_model.Scholarship.query.first()
        questions = question_model.Question.query.filter(
            question_model.Question.id.in_((1, 2)))

        for question in questions:
            scholarship.add_boolean_requirement(question, 1)

        application.db.session.commit()

        response = client.get("/api/scholarships/1/boolean_requirement")

        assert response.status_code == 200
        assert response.get_json() == [
            requirement.to_dict()
            for requirement in scholarship.boolean_requirement.all()
        ]
