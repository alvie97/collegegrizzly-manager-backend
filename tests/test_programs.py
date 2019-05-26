from app import db
from app.models.qualification_round import QualificationRound
from app.models.program import Program
from app.models.association_tables import program_qualification_round

url = "/api/programs"


def test_get_programs(app, client, auth):
    """ get all programs and test search function """

    # create programs to test

    programs_properties = []

    with app.app_context():
        for i in range(50):

            programs_properties.append({"name": f"test program {i}"})

            program = Program(**programs_properties[i])
            db.session.add(program)

        db.session.commit()

    # login

    auth.login()

    # get programs

    response = client.get(url)
    data = response.get_json()
    programs = data["items"]

    for i, program in enumerate(programs):
        assert program["name"] == programs_properties[i]["name"]

    # get program that ends with "or 2"

    response = client.get(url + "?search=am 2")
    data = response.get_json()
    programs = data["items"]

    assert len(programs) > 0

    for program in programs:
        assert program["name"].find("am 2") != -1


def test_create_program(app, client, auth):
    """creates program"""

    auth.login()

    # create program

    data = {"name": "test post program"}

    response = client.post(url, json=data)
    response_data = response.get_json()
    program_url = response_data["program"]

    response = client.get(program_url)
    response_data = response.get_json()

    with app.test_request_context():
        program = Program.get(response_data["id"])

        assert program is not None
        assert program.to_dict() == response_data


def test_patch_program(app, client, auth):
    # update program

    auth.login()

    patch_data = {
        "name": "test patch program",
        "description": "test description"
    }

    with app.app_context():
        program = Program(name="test program")
        db.session.add(program)
        db.session.commit()
        program_id = program.id

        response = client.patch(url + f"/{program_id}", json=patch_data)

    response_data = response.get_json()
    program_url = response_data["program"]

    response = client.get(program_url)
    response_data = response.get_json()

    with app.app_context():
        program = Program.get(response_data["id"])

        assert program is not None
        assert program.name == patch_data["name"]


def test_delete_program(app, client, auth):
    """ create programs and edit them"""

    # delete program
    auth.login()

    with app.app_context():
        program = Program(name="test program")
        db.session.add(program)
        db.session.commit()

        client.delete(url + f"/{program.id}")

        program = Program.get(program.id)

        assert program is None


def test_program_qualification_rounds(app, client, auth):
    """ tests add, read and remove qualification_rounds """
    auth.login()

    with app.app_context():
        program = Program(name="test program")
        db.session.add(program)

        for i in range(5):
            db.session.add(
                QualificationRound(name=f"test qualification_round {i}"))

        db.session.commit()

        response = client.post(
            url + f"/{program.id}/qualification_rounds",
            json=[x for x in range(5)])

        assert program.qualification_rounds.count() == 5

        assert response.status_code == 200

    qualification_rounds_url = response.get_json()["qualification_rounds"]

    response = client.get(qualification_rounds_url)

    qualification_rounds = response.get_json()["items"]

    assert len(qualification_rounds) > 0

    with app.app_context():
        program = Program.query.first()
        for qualification_round in qualification_rounds:
            assert program.qualification_rounds.filter(
                program_qualification_round.c.qualification_round_id ==
                qualification_round["id"]) > 0

    response = client.delete(
        url + f"/{program.id}/qualification_rounds",
        json=[x for x in range(3)])

    qualification_rounds_url = response.get_json()["qualification_rounds"]

    response = client.get(qualification_rounds_url)

    qualification_rounds = response.get_json()["items"]

    assert len(qualification_rounds) > 0

    with app.app_context():
        program = Program.query.first()
        assert program.qualification_rounds.count() == 2

        for qualification_round in qualification_rounds:
            assert program.qualification_rounds.filter(
                program_qualification_round.c.qualification_round_id ==
                qualification_round["id"]) > 0