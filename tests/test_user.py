# improve user tests
from app.schemas import user_schema
from app.models import user as user_model
import marshmallow
import flask
import app as application
import pytest

url = "/api/users"


def test_user_schema(app, client, auth):
    """
    Tests user schema
    """

    user_schema_test = user_schema.UserSchema()

    user_info = {"username": "test_user"}

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)

    assert err.value.messages["password"][0] == "password required"
    assert err.value.messages["email"][0] == "email required"
    assert err.value.messages["first_name"][0] == "first name required"
    assert err.value.messages["last_name"][0] == "last name required"
    assert err.value.messages["role"][0] == "role required"

    user_info = {
        "username": "test_user" * 120,
        "email": "test_user@example.com",
        "first_name": "test first name",
        "last_name": "test last name",
        "password": "Te$t0",
        "role": "administrator"
    }

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)

    assert err.value.messages["username"][
        0] == "username must be shorter than 120 characters"

    user_info["username"] = "a"
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["username"][
        0] == "username must be at least 4 characters long"

    user_info["username"] = ".test_username"
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["username"][0] == "invalid username"

    user_info["username"] = "test._username"
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["username"][0] == "invalid username"

    user_info["username"] = "test__username"
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["username"][0] == "invalid username"

    user_info["username"] = "test_.username"
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["username"][0] == "invalid username"

    user_info["username"] = "test..username"
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["username"][0] == "invalid username"

    user_info["username"] = "testusername._"
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["username"][0] == "invalid username"

    user_info["username"] = "testusername."
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["username"][0] == "invalid username"

    user_info["username"] = "testusername_"
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["username"][0] == "invalid username"

    user_info["username"] = "test_user"
    user_info["password"] = "a"

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["password"][
        0] == "password must be at least 8 characters long"

    user_info["password"] = "a" * 8

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["password"][
        0] == "password must have at least 1 uppercase character"

    user_info["password"] = "Aa" * 4

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["password"][
        0] == "password must have at least 1 number character"

    user_info["password"] = "AA1234aa"

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["password"][
        0] == "password must have at least 1 special character"

    user_info["password"] = "AA1234aa"

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["password"][
        0] == "password must have at least 1 special character"

    user_info["password"] = "AA1234234$"

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["password"][
        0] == "password must have at least 1 lowercase character"

    user_info["password"] = "AA12aaa234$"
    user_info["email"] = "asdfasdf"

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["email"][0] == "invalid email"

    user_info["email"] = "a@ a . com"

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["email"][0] == "invalid email"

    user_info["email"] = "a @a.com"

    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["email"][0] == "invalid email"

    user_info["email"] = "example@example.com"
    user_info["first_name"] = "a" * 300
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["first_name"][
        0] == "first name must be shorter than 256 characters"

    user_info["first_name"] = "test name"
    user_info["last_name"] = "a" * 300
    with pytest.raises(marshmallow.ValidationError) as err:
        user_schema_test.load(user_info)
    assert err.value.messages["last_name"][
        0] == "last name must be shorter than 256 characters"


def test_create_user_success(app, client, auth):
    """
    Tests create_user endpoint success.
    """

    json = {
        "username": "test_user",
        "email": "test_user@example.com",
        "first_name": "test first name",
        "last_name": "test last name",
        "password": "AA12aaa234$",
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


def test_create_user_failure(app, client, auth):
    """
    Tests create_user endpoint failure cases
    """

    auth.login()

    user_info = []

    response = client.post(url, json=user_info)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    user_info = {}

    response = client.post(url, json=user_info)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    user_info = {
        "username": "test_user" * 120,
        "email": "test_user@example.com",
        "first_name": "test first name",
        "last_name": "test last name",
        "role": "administrator"
    }

    response = client.post(url, json=user_info)
    assert response.status_code == 400

    response_errors = response.get_json()
    assert response_errors["username"][
        0] == "username must be shorter than 120 characters"
    assert response_errors["password"][0] == "password required"

    with app.app_context():
        assert user_model.User.query.count() == 1


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


def test_edit_user_failure(app, client, auth):
    """
    Tests edit_user endpoint failure cases.
    """
    user_info = {
        "username": "test_user",
        "email": "test_user@example.com",
        "first_name": "test first name",
        "last_name": "test last name",
        "password": "AA12aaa234$",
        "role": "administrator"
    }

    with app.app_context():
        user = user_model.User(**user_info)
        application.db.session.add(user)
        application.db.session.commit()

    auth.login()

    user_info_edit = {"username": "test_.__adsf"}

    response = client.patch(
        url + f"/{user_info['username']}", json=user_info_edit)
    assert response.status_code == 400

    response_json = response.get_json()
    assert response_json["username"][0] == "invalid username"

    with app.app_context():
        user_count = user_model.User.query.filter_by(
            username=user_info_edit['username']).count()
        assert user_count == 0
        user_count = user_model.User.query.filter_by(
            username=user_info['username']).count()
        assert user_count == 1


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


def test_delete_user_failure(app, client, auth):
    """
    Tests delete_user endpoint failure cases.
    """

    auth.login()

    response = client.delete(url + "/____user_not_found___")
    assert response.status_code == 404


def test_get_user_success(app, client, auth):
    """
    Test get user success
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

    response = client.get(url + f"/{user_info['username']}")
    assert response.status_code == 200

    response_json = response.get_json()

    with app.test_request_context():
        user = user_model.User.query.filter_by(
            username=user_info["username"]).first()
        assert response_json["user"] == user.to_dict()


def test_get_user_failure(app, client, auth):
    """
    Tests get_user endpoint failure cases.
    """

    auth.login()

    response = client.get(url + "/____user_not_found___")
    assert response.status_code == 404


def test_get_users(app, client, auth):
    """ get all users and test search function """

    user_info = {
        "first_name": "test first name",
        "last_name": "test last name",
        "password": "Te$t0",
        "role": "administrator"
    }

    with app.app_context():
        for i in range(50):
            user_info["username"] = f"test_user_{i}"
            user_info["email"] = f"test_user_{i}@example.com"
            user = user_model.User(**user_info)
            application.db.session.add(user)

        application.db.session.commit()

    auth.login()

    response = client.get(url)

    assert response.status_code == 200

    data = response.get_json()
    users = data["items"]

    assert len(users) > 0

    for i, user in enumerate(users):
        assert user["username"] == f"test_user_{i}"

    response = client.get(url + "?search=test_user_2")
    data = response.get_json()
    users = data["items"]

    assert len(users) > 0

    for user in users:
        assert user["username"].find("test_user_2") != -1