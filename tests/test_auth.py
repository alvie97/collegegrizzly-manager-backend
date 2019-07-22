# TODO: add failure tests
# TODO: test route protection with jwt
# TODO: test util functions from app/security/utils.py
# TODO: change imports
import app as application
from app.security import revoke_token
from flask_jwt_extended import decode_token, set_refresh_cookies
from app.models import token_blacklist
from tests.helpers import get_cookie, get_raw_cookie
import time

url = "/auth"


def test_login_success(app, client, user):
    """
    tests login endpoint success cases
    """
    json = {"id": "test", "password": "test"}

    response = client.post(url + "/login", json=json)
    assert response.status_code == 200
    assert response.get_json()["login"] == True

    access_token = get_cookie(response, app.config["JWT_ACCESS_COOKIE_NAME"])
    refresh_token = get_cookie(response, app.config["JWT_REFRESH_COOKIE_NAME"])

    with app.app_context():
        access_token = decode_token(access_token)
        refresh_token = decode_token(refresh_token)

        assert access_token[app.config["JWT_IDENTITY_CLAIM"]] == json["id"]
        assert refresh_token[app.config["JWT_IDENTITY_CLAIM"]] == json["id"]

        user_tokens = token_blacklist.TokenBlacklist.query.filter_by(
            user=json["id"], jti=refresh_token["jti"], revoked=False).count()
        assert user_tokens == 1


def test_login_failure(app, client, user):
    """
    Tests login endpoint failure cases
    """
    response = client.post(url + "/login", json=[])
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"
    response = client.post(url + "/login", json={})
    assert response.get_json(
    )["message"] == "no data provided or bad structure"

    response = client.post(url + "/login", json={"password": "test"})
    assert response.status_code == 400
    assert response.get_json()["message"] == "no username or email provided"
    response = client.post(url + "/login", json={"id": "asdf"})
    assert response.status_code == 400
    assert response.get_json()["message"] == "no password provided"
    response = client.post(
        url + "/login", json={
            "id": "asdf",
            "password": "asdf"
        })
    assert response.status_code == 404
    assert response.get_json(
    )["message"] == f"no user with username or email asdf found"
    response = client.post(
        url + "/login", json={
            "id": "test",
            "password": "asdf"
        })
    assert response.status_code == 401
    assert response.get_json()["message"] == "invalid credentials"


def test_refresh_token(app, client, user):
    """
    Tests refresh_token endpoint
    """

    json = {"id": "test", "password": "test"}

    response = client.post(url + "/login", json=json)
    assert response.status_code == 200
    assert response.get_json()["login"] == True

    access_token = get_cookie(response, app.config["JWT_ACCESS_COOKIE_NAME"])

    time.sleep(2)

    response = client.post(url + "/token/refresh")
    assert response.status_code == 200
    assert response.get_json()["refreshed"] == True

    refresh_access_token = get_cookie(response,
                                      app.config["JWT_ACCESS_COOKIE_NAME"])

    assert access_token != refresh_access_token

    with app.app_context():
        access_token = decode_token(access_token)
        refresh_access_token = decode_token(refresh_access_token)

        assert access_token["jti"] != refresh_access_token["jti"]
        assert access_token["exp"] < refresh_access_token["exp"]


def test_refresh_token_failure(app, client, user):
    """
    tests refresh_token endpoint, failure cases
    """
    response = client.post(url + "/token/refresh")
    assert response.status_code == 422
    assert response.get_json()["message"] == "invalid token"

    json = {"id": "test", "password": "test"}

    response = client.post(url + "/login", json=json)
    assert response.status_code == 200
    assert response.get_json()["login"] == True

    time.sleep(7)

    response = client.post(url + "/token/refresh")
    assert response.status_code == 401
    assert response.get_json()["message"] == "expired token"

    json = {"id": "test", "password": "test"}

    response = client.post(url + "/login", json=json)
    assert response.status_code == 200
    assert response.get_json()["login"] == True

    refresh_token = get_cookie(response, app.config["JWT_REFRESH_COOKIE_NAME"])

    client.set_cookie(
        "localhost",
        app.config["JWT_REFRESH_COOKIE_NAME"],
        "",
        path=app.config["JWT_REFRESH_COOKIE_PATH"])
    response = client.post(url + "/token/refresh")
    assert response.status_code == 422
    assert response.get_json()["message"] == "invalid token"

    client.set_cookie(
        "localhost",
        app.config["JWT_REFRESH_COOKIE_NAME"],
        refresh_token[2:],
        path=app.config["JWT_REFRESH_COOKIE_PATH"])
    response = client.post(url + "/token/refresh")
    assert response.status_code == 422
    assert response.get_json()["message"] == "invalid token"

    client.set_cookie(
        "localhost",
        app.config["JWT_REFRESH_COOKIE_NAME"],
        refresh_token,
        path=app.config["JWT_REFRESH_COOKIE_PATH"])
    response = client.post(url + "/token/refresh")
    assert response.status_code == 200
    assert response.get_json()["refreshed"] == True

    with app.app_context():
        refresh_token = decode_token(refresh_token)
        token = token_blacklist.TokenBlacklist.query.filter_by(
            jti=refresh_token["jti"]).first()
        revoke_token(token)
        application.db.session.commit()

    response = client.post(url + "/token/refresh")
    assert response.status_code == 401
    assert response.get_json()["message"] == "revoked token"


def test_logout_success(app, client, user):
    """
    Tests logout success cases
    """
    json = {"id": "test", "password": "test"}

    response = client.post(url + "/login", json=json)
    assert response.status_code == 200
    assert response.get_json()["login"] == True

    refresh_token = get_cookie(response, app.config["JWT_REFRESH_COOKIE_NAME"])

    response = client.post(url + "/logout")
    assert response.status_code == 200
    assert response.get_json()["logout"] == True

    cookie = get_cookie(response, app.config["JWT_ACCESS_COOKIE_NAME"])
    assert cookie == ""
    cookie = get_cookie(response, app.config["JWT_REFRESH_COOKIE_NAME"])
    assert cookie == ""

    with app.app_context():
        refresh_token = decode_token(refresh_token)

        user_token = token_blacklist.TokenBlacklist.query.filter_by(
            user=json["id"], jti=refresh_token["jti"]).first()

        assert user_token.revoked == True


def test_logout_all_success(app, client, user):
    """
    Tests logout_all success cases
    """
    json = {"id": "test", "password": "test"}

    response = client.post(url + "/login", json=json)
    assert response.status_code == 200
    assert response.get_json()["login"] == True

    response = client.post(url + "/login", json=json)
    assert response.status_code == 200
    assert response.get_json()["login"] == True

    with app.app_context():
        tokens_count = token_blacklist.TokenBlacklist.query.filter_by(
            user=json["id"], revoked=False).count()
        assert tokens_count == 2

    response = client.post(url + "/logout/all")
    assert response.status_code == 200
    assert response.get_json()["logout"] == True

    cookie = get_cookie(response, app.config["JWT_ACCESS_COOKIE_NAME"])
    assert cookie == ""
    cookie = get_cookie(response, app.config["JWT_REFRESH_COOKIE_NAME"])
    assert cookie == ""

    with app.app_context():
        tokens_count = token_blacklist.TokenBlacklist.query.filter_by(
            user=json["id"], revoked=False).count()
        assert tokens_count == 0