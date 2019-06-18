# TODO: add failure tests
# TODO: change imports
import app as application
from flask_jwt_extended import decode_token
from app.models import token_blacklist
from tests.helpers import get_cookie
import time

url = "/auth"


def test_login_success(app, client, user):
    """
    tests login endpoint successfull
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