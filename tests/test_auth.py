from flask import g

from app import db
from app.models.user import User
from helpers import get_cookie


def test_login(app, client):

    with app.app_context():
        user = User(
            username="test",
            email="test@test.com",
            password="test",
            role="administrator")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/auth/login", data={
            "id": "test",
            "password": "test"
        })

    assert response.status_code == 302
    assert get_cookie(response, app.config["ACCESS_TOKEN_COOKIE_NAME"])
    assert get_cookie(response, app.config["REFRESH_TOKEN_COOKIE_NAME"])


def test_logout(app, client):
    with app.app_context():
        user = User(username="test", email="test@test.com", password="test")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/auth/login", data={
            "id": "test",
            "password": "test"
        })

    access_token = get_cookie(response, app.config["ACCESS_TOKEN_COOKIE_NAME"])
    refresh_token = get_cookie(response,
                               app.config["REFRESH_TOKEN_COOKIE_NAME"])
    client.set_cookie(
        "localhost",
        app.config["ACCESS_TOKEN_COOKIE_NAME"],
        access_token,
        httponly=True)
    client.set_cookie(
        "localhost",
        "refresh_token",
        app.config["REFRESH_TOKEN_COOKIE_NAME"],
        httponly=True)
    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert not get_cookie(response, app.config["ACCESS_TOKEN_COOKIE_NAME"])
    assert not get_cookie(response, app.config["REFRESH_TOKEN_COOKIE_NAME"])
    # assert not get_cookie(response, "x-csrf-token")
