import app as application
from app.models import question as question_model
from app.models import option as option_model
from app.models import association_tables

url = "/api/options"


def test_option_database_schema(app):
    """
    Tests option database schema
    """

    with app.app_context():
        for i in range(5):
            option = option_model.Option(name=f"test option {i}")
            application.db.session.add(option)

        application.db.session.commit()

        assert option_model.Option.query.count() == 5


def test_api_endpoints_get_options(app, auth, client, options):
    """
    Tests get_options endpoint
    """

    auth.login()

    response = client.get(url)
    data = response.get_json()
    options = data["items"]

    with app.app_context():
        for option in options:
            assert option_model.Option.query.filter_by(
                id=option["id"], name=option["name"]).count() == 1

    response = client.get(url + "?search=on test 2")
    data = response.get_json()
    options = data["items"]

    assert len(options) > 0

    for option in options:
        assert option["name"].find("on test 2") != -1


def test_api_endpoints_create_option_success(app, auth, client):
    """
    Tests create_option endpoint success cases
    """
    auth.login()

    json = {"name": "test option 1"}
    response = client.post(url, json=json)

    assert response.status_code == 201
    assert response.get_json()["message"] == "option created"

    with app.app_context():
        query_obj = option_model.Option.query
        assert query_obj.count() == 1
        assert query_obj.filter_by(name=json["name"])


def test_api_endpoints_create_option_failure(app, auth, client):
    """
    Tests create_option endpoint failure cases
    """
    with app.app_context():
        option = option_model.Option(name=f"test option 1")
        application.db.session.add(option)
        application.db.session.commit()

    auth.login()

    json = [1]
    response = client.post(url, json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    json = {}
    response = client.post(url, json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    json = {"name": "test option 1"}
    response = client.post(url, json=json)
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == f"option '{json['name']}' already exists"

    with app.app_context():
        assert option_model.Option.query.count() == 1


def test_api_endpoints_delete_option_success(app, auth, client):
    """
    Tests delete_option endpoint sucess cases
    """
    with app.app_context():
        option = option_model.Option(name=f"test option 1")
        application.db.session.add(option)
        application.db.session.commit()

        assert option_model.Option.query.count() == 1

    auth.login()

    response = client.delete(url + "/1")
    assert response.status_code == 200
    assert response.get_json()["message"] == "option deleted"

    with app.app_context():
        assert option_model.Option.query.count() == 0


def test_api_endpoints_delete_option_failure(app, auth, client):
    """
    Tests delete_option endpoint failure cases
    """
    with app.app_context():
        option = option_model.Option(name=f"test option 1")
        application.db.session.add(option)
        application.db.session.commit()

        assert option_model.Option.query.count() == 1

    auth.login()

    response = client.delete(url + "/9999")
    assert response.status_code == 404

    with app.app_context():
        assert option_model.Option.query.count() == 1


def test_api_endpoints_get_questions_success(app, client, auth, options,
                                             questions):
    """
    Tests get option questions success cases
    """

    with app.app_context():
        option = option_model.Option.query.first()
        questions_array = question_model.Question.query.limit(5)

        for question in questions_array:
            question.add_option(option)

        application.db.session.commit()

    auth.login()

    response = client.get(url + "/1/questions")

    assert response.status_code == 200

    json_response = response.get_json()["items"]

    with app.app_context():
        option = option_model.Option.query.first()

        for question in json_response:
            assert option.questions.filter(
                association_tables.question_option.c.question_id ==
                question["id"]).count() > 0
