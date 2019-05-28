import os
import tempfile

import pytest

from app import create_app, db
from app.utils import generate_public_id
from app.models.college import College
from app.models.college_details import CollegeDetails
from app.models.grade import Grade
from app.models.scholarship_details import ScholarshipDetails
from app.models.question import Question
from app.models.user import User
from app.models.grade_requirement_group import GradeRequirementGroup
from config import Config
from app.models.scholarship import Scholarship
from app.models.program import Program
from app.models.qualification_round import QualificationRound
from app.models.association_tables import ProgramRequirement
from app.models import question as question_model
from app.models import option as option_model


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
            first_name="test name",
            last_name="test last name",
            password="test",
            role="administrator")
        db.session.add(user)
        db.session.commit()
    return AuthActions(client)


@pytest.fixture
def programs_requirement(app):
    with app.app_context():
        scholarship = Scholarship()
        db.session.add(scholarship)
        program = Program(name="test program")
        program_1 = Program(name="test program 1")

        db.session.add(program)

        for i in range(4):
            q_round = QualificationRound(name=f"test qualification round {i}")
            db.session.add(q_round)
            if i <= 3:
                program.add_qualification_round(q_round)
            else:
                program_1.add_qualification_round(q_round)

        program_requirement = ProgramRequirement(program=program)
        program_requirement.qualification_rounds.append(
            program.qualification_rounds.first())

        scholarship.programs_requirement.append(program_requirement)

        db.session.commit()


@pytest.fixture
def colleges(app):
    with app.app_context():
        for i in range(10):
            college_details = CollegeDetails(name=f"test college {i}")
            college = College(college_details=college_details)
            db.session.add(college_details)
            db.session.add(college)

        db.session.commit()


@pytest.fixture
def scholarships(app):
    with app.app_context():
        for i in range(10):
            scholarship_details = ScholarshipDetails(
                name=f"test scholarship {i}")
            scholarship = Scholarship(scholarship_details=scholarship_details)
            db.session.add(scholarship_details)
            db.session.add(scholarship)

        db.session.commit()


@pytest.fixture
def questions(app):
    with app.app_context():
        for i in range(10):
            question = Question(name=f"test question {i}")
            db.session.add(question)

        db.session.commit()


@pytest.fixture
def grades(app):
    with app.app_context():
        for i in range(10):
            grade = Grade(name=f"test grade {i}", min=10, max=20)
            db.session.add(grade)

        db.session.commit()


@pytest.fixture
def groups(app):
    with app.app_context():
        for i in range(10):
            group = GradeRequirementGroup()
            db.session.add(group)

        db.session.commit()


@pytest.fixture
def questions(app):
    with app.app_context():
        for i in range(5):
            db.session.add(question_model.Question(name=f"question test {i}"))
            db.session.commit()


@pytest.fixture
def options(app):
    with app.app_context():
        for i in range(5):
            db.session.add(option_model.Option(name=f"option test {i}"))
            db.session.commit()