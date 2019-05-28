# improve user tests
from app.models import user as user_model
import flask
import app as application

url = "/api/users"


def test_create_user_success(app, client, auth):
    """
    Tests create_user endpoint success.
    """

    json = {
        "username": "test_user",
        "email": "test_user@example.com",
        "first_name": "test first name",
        "last_name": "test last name",
        "password": "Te$t0",
        "role": "administrator"
    }

    auth.login()

    response = client.post(url, json=json)

    assert response.status_code == 201
    response_json = response.get_json()

    with app.test_request_context():
        assert response_json["user"] == flask.url_for(
            "users.get_user", username=json["username"])

    with app.app_context():
        assert user_model.User.query.filter_by(
            username=json["username"]).count() == 1


def test_edit_user_success(app, client, auth):
    """
    Tests edit_user endpoint success.
    """

    user_info = {
        "username": "test_user",
        "email": "test_user@example.com",
        "first_name": "test first name",
        "last_name": "test last name",
        "password": "Te$t0",
        "role": "administrator"
    }

    with app.app_context():
        user = user_model.User(**user_info)
        application.db.session.add(user)
        application.db.session.commit()

    auth.login()

    json = {"email": "email_edit@example.com"}

    response = client.patch(url + f"/{user_info['username']}", json=json)

    assert response.status_code == 200
    response_json = response.get_json()

    with app.test_request_context():
        assert response_json["user"] == flask.url_for(
            "users.get_user", username=user_info["username"])

    with app.app_context():
        assert user_model.User.query.filter_by(
            username=user_info["username"]).count() == 1
        assert user_model.User.query.filter_by(
            username=user_info["username"], email=json["email"]).count() == 1


def test_delete_user_success(app, client, auth):
    """
    Tests delete_user endpoint success.
    """

    user_info = {
        "username": "test_user",
        "email": "test_user@example.com",
        "first_name": "test first name",
        "last_name": "test last name",
        "password": "Te$t0",
        "role": "administrator"
    }

    with app.app_context():
        user = user_model.User(**user_info)
        application.db.session.add(user)
        application.db.session.commit()

        assert user_model.User.query.filter_by(
            username=user_info["username"]).count() == 1

    auth.login()

    response = client.delete(url + f"/{user_info['username']}")

    assert response.status_code == 200
    assert response.get_json()["message"] == "user deleted"

    with app.app_context():
        assert user_model.User.query.filter_by(
            username=user_info["username"]).count() == 0