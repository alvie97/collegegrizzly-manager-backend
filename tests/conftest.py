import os
import tempfile

import pytest

from app import create_app, db
from app.utils import generate_public_id
from app.models.college import College
from app.models.user import User
from config import Config


@pytest.fixture
def app():
    DB_FD, DB_URL = tempfile.mkstemp()

    class TestConfig(Config):
        TESTING = True
        ACCESS_COOKIE_NAME = "access_token"
        REFRESH_COOKIE_NAME = "refresh_token"
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_URL

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

    yield app

    os.close(DB_FD)
    os.unlink(DB_URL)


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions(object):

    def __init__(self, client, csrf_token=""):
        self._client = client
        self._csrf_token = csrf_token

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={
                "id": username,
                "password": password
            })

    def logout(self):
        return self._client.get(
            "/auth/logout", headers={"X-XSRF-TOKEN": self._csrf_token})


@pytest.fixture
def auth(app, client):
    with app.app_context():
        user = User(
            username="test",
            email="test@test.com",
            password="test",
            role="administrator")
        db.session.add(user)
        db.session.commit()
    return AuthActions(client)
