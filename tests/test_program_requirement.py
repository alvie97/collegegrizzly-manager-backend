from app.models.program import Program
from app.models.qualification_round import QualificationRound
from app.models.scholarship import Scholarship
from app.models.association_tables import ProgramRequirement
from app import db
from uuid import uuid4


def test_program_requirement(app):
    with app.app_context():
        scholarship = Scholarship()
        db.session.add(scholarship)
        for i in range(2):
            program = Program(name=f"test program {i}")
            db.session.add(program)
            for j in range(2):
                qualification_round = QualificationRound(
                    name="qualification round " + str(uuid4()))
                db.session.add(qualification_round)
                program.add_qualification_round(qualification_round)

        programs = Program.get_all()

        program_requirement = ProgramRequirement(program=programs[0])
        for qualification_round in programs[0].qualification_rounds:
            program_requirement.qualification_rounds.append(
                qualification_round)

        scholarship.programs_requirement.append(program_requirement)

        program_requirement = ProgramRequirement(program=programs[1])
        program_requirement.qualification_rounds.append(
            programs[1].qualification_rounds.first())
        scholarship.programs_requirement.append(program_requirement)

        db.session.commit()

        scholarship = Scholarship.query.first()

        assert scholarship.programs_requirement.count() == 2

        programs_requirement = scholarship.programs_requirement.all()

        assert programs_requirement[0].program.name == programs[0].name
        assert programs_requirement[0].qualification_rounds.count() == 2

        for i, qualification_round in enumerate(
                programs_requirement[0].qualification_rounds.all()):
            assert programs[0].qualification_rounds.filter_by(
                name=qualification_round.name).first() is not None

        qualification_rounds = programs[1].qualification_rounds.all()

        assert programs_requirement[1].program.name == programs[1].name
        assert programs_requirement[1].qualification_rounds.count() == 1
        qualification_round = programs_requirement[
            1].qualification_rounds.first()
        assert qualification_round.name == qualification_rounds[0].name


def test_add_programs_requirement_to_scholarship(app, auth, client):
    auth.login()

    with app.app_context():
        scholarship = Scholarship()
        db.session.add(scholarship)
        for i in range(2):
            program = Program(name=f"test program {i}")
            db.session.add(program)
            for j in range(2):
                qualification_round = QualificationRound(
                    name="qualification round " + str(uuid4()))
                db.session.add(qualification_round)
                program.add_qualification_round(qualification_round)
        db.session.commit()

        programs = Program.get_all()

        program_requirement_json = [{
            "program_id": programs[0].id,
            "qualification_rounds": []
        }, {
            "program_id": programs[1].id,
            "qualification_rounds": []
        }]

        for qualification_round in programs[0].qualification_rounds:
            program_requirement_json[0]["qualification_rounds"].append(
                qualification_round.id)

        program_requirement_json[1]["qualification_rounds"].append(
            programs[1].qualification_rounds.first().id)

        response = client.post(
            f"/api/scholarships/{scholarship.id}/programs_requirement",
            json=program_requirement_json)

        assert response.status_code == 200

    with app.app_context():
        scholarship = Scholarship.query.first()
        programs = Program.get_all()

        assert scholarship.programs_requirement.count() == 2

        programs_requirement = scholarship.programs_requirement.all()

        assert programs_requirement[0].program.name == programs[0].name
        assert programs_requirement[0].qualification_rounds.count() == 2

        for i, qualification_round in enumerate(
                programs_requirement[0].qualification_rounds.all()):
            assert programs[0].qualification_rounds.filter_by(
                name=qualification_round.name).first() is not None

        qualification_rounds = programs[1].qualification_rounds.all()

        assert programs_requirement[1].program.name == programs[1].name
        assert programs_requirement[1].qualification_rounds.count() == 1
        qualification_round = programs_requirement[
            1].qualification_rounds.first()
        assert qualification_round.name == qualification_rounds[0].name


def test_get_program_requirement_from_program_id(app):
    with app.app_context():
        scholarship = Scholarship()
        db.session.add(scholarship)
        for i in range(2):
            program = Program(name=f"test program {i}")
            db.session.add(program)
            for j in range(2):
                qualification_round = QualificationRound(
                    name="qualification round " + str(uuid4()))
                db.session.add(qualification_round)
                program.add_qualification_round(qualification_round)

        programs = Program.get_all()

        program_requirement = ProgramRequirement(program=programs[0])
        for qualification_round in programs[0].qualification_rounds:
            program_requirement.qualification_rounds.append(
                qualification_round)

        scholarship.programs_requirement.append(program_requirement)

        program_requirement = ProgramRequirement(program=programs[1])
        program_requirement.qualification_rounds.append(
            programs[1].qualification_rounds.first())
        scholarship.programs_requirement.append(program_requirement)

        db.session.commit()

        scholarship = Scholarship.query.first()

        programs_requirement = scholarship.programs_requirement.filter(
            ProgramRequirement.id == ProgramRequirement.first().id)

        print(
            programs_requirement.statement.compile(
                compile_kwargs={"literal_binds": True}))

        assert programs_requirement.count() == 1


# failure cases


def test_add_qualification_rounds_scholarships_failure_0(
        app, client, auth, programs_requirement):
    """json data is empty"""
    auth.login()
    url = "/api/scholarships/1/programs_requirement/1/qualification_rounds"
    json = []
    response = client.post(url, json=json)

    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"


def test_add_qualification_rounds_scholarships_failure_1(
        app, client, auth, programs_requirement):
    """json is not a list"""
    auth.login()
    url = "/api/scholarships/1/programs_requirement/1/qualification_rounds"
    json = "not a list"
    response = client.post(url, json=json)
    assert response.status_code == 400
    assert response.get_json(
    )["message"] == "no data provided or bad structure"


def test_add_qualification_rounds_scholarships_failure_2(
        app, client, auth, programs_requirement):
    """scholarship is not found"""
    auth.login()
    json = [1, 3]
    response = client.post(
        "/api/scholarships/10000/programs_requirement/1"
        "/qualification_rounds",
        json=json)

    assert response.status_code == 404
    assert response.get_json()["message"] == "resource not found"


def test_add_qualification_rounds_scholarships_failure_3(
        app, client, auth, programs_requirement):
    """scholarship doesn't have program requirement with given program id"""
    auth.login()
    json = [1, 3]
    response = client.post(
        "/api/scholarships/1/programs_requirement/1000"
        "/qualification_rounds",
        json=json)

    assert response.status_code == 404
    assert response.get_json()["message"] == "resource not found"


def test_add_qualification_rounds_scholarships_failure_4(
        app, client, auth, programs_requirement):
    """qualification round id in list is not an integer"""
    auth.login()
    url = "/api/scholarships/1/programs_requirement/1/qualification_rounds"
    json = [1, "test integer"]
    response = client.post(url, json=json)
    assert response.status_code == 400
    assert response.get_json()["message"] == "invalid qualification round id"


def test_add_qualification_rounds_scholarships_failure_5(
        app, client, auth, programs_requirement):
    """qualification round not found"""
    auth.login()
    json = [1, 10]
    url = "/api/scholarships/1/programs_requirement/1/qualification_rounds"
    response = client.post(url, json=json)
    assert response.status_code == 404
    assert response.get_json(
    )["message"] == f"program does not have qualification round {json[1]}"


def test_add_qualification_rounds_scholarships_failure_6(
        app, client, auth, programs_requirement):
    """rounds aren't stored in database on error"""
    auth.login()
    json = [2, 10]
    url = "/api/scholarships/1/programs_requirement/1/qualification_rounds"
    client.post(url, json=json)
    with app.app_context():
        scholarship = Scholarship.query.first()
        program_requirement = scholarship.programs_requirement.first()
        scholarship_qualification_rounds_count = program_requirement \
            .qualification_rounds.count()

        assert scholarship_qualification_rounds_count == 1


# success cases
def test_add_qualification_rounds_scholarships_success_0(
        app, client, auth, programs_requirement):
    """qualification rounds added successfully"""
    auth.login()
    json = [2, 3]
    url = "/api/scholarships/1/programs_requirement/1/qualification_rounds"
    response = client.post(url, json=json)
    assert response.status_code == 200
    assert response.get_json()["message"] == "qualification rounds added"
    with app.app_context():
        scholarship = Scholarship.query.first()
        program_requirement = scholarship.programs_requirement.first()
        scholarship_qualification_rounds_count = program_requirement \
            .qualification_rounds.count()

        assert scholarship_qualification_rounds_count == 3


def test_add_qualification_rounds_scholarships_success_1(
        app, client, auth, programs_requirement):
    """one or more qualification rounds already exist in program requirement"""
    auth.login()
    json = [1, 3]
    url = "/api/scholarships/1/programs_requirement/1/qualification_rounds"
    response = client.post(url, json=json)
    assert response.status_code == 200
    assert response.get_json()["message"] == "qualification rounds added"
    with app.app_context():
        scholarship = Scholarship.query.first()
        program_requirement = scholarship.programs_requirement.first()
        scholarship_qualification_rounds_count = program_requirement \
            .qualification_rounds.count()

        assert scholarship_qualification_rounds_count == 2
