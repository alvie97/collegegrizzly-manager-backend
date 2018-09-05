from app import create_app, db
from app.common.utils import generate_public_id
from app.models.college import College
from app.models.scholarship import Scholarship
from config import Config
from subprocess import run
import os
import pytest
import tempfile


@pytest.fixture
def app():
  DB_FD, DB_URL = tempfile.mkstemp()

  class TestConfig(Config):
    TESTING = True
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


@pytest.fixture
def college_id(app):
  with app.app_context():
    college = College(public_id=generate_public_id(), name="test college")
    db.session.add(college)
    db.session.commit()

    return college.public_id


@pytest.fixture
def scholarship_id(app, college_id):
  with app.app_context():
    college = College.first(public_id=college_id)
    scholarship = Scholarship(
        public_id=generate_public_id(),
        college=college,
        name="test scholarship")
    db.session.add(scholarship)
    db.session.commit()

    return scholarship.public_id

# @pytest.fixture(scope="session")
# def locations(app):
#   with app.app_context():
#     run(["flask", "geocodes", "save_in_database"])

#     result = db.engine.execute("SELECT COUNT(*) FROM state")
#     assert result.scalar() > 1
