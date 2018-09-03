from app import create_app, db
from config import Config
import os
import pytest
import tempfile



@pytest.fixture
def app():
  DB_FD, DB_URL = tempfile.mkstemp()

  class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI="sqlite:///" + DB_URL

  app = create_app(TestConfig)

  with app.app_context():
    db.create_all()

  yield app

  os.close(DB_FD)
  os.unlink(DB_URL)

@pytest.fixture
def client(app):
  return app.test_client()
