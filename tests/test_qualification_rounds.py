from app import db
from app.models.qualification_round import QualificationRound
from app.models.program import Program

url = "/api/qualification_rounds"


def test_get_qualification_rounds(app, client, auth):
    """ get all qualification_rounds and test search function """

    # create qualification_rounds to test

    qualification_rounds_properties = []

    with app.app_context():
        for i in range(50):

            qualification_rounds_properties.append({
                "name":
                f"test qualification_round {i}"
            })

            qualification_round = QualificationRound(
                **qualification_rounds_properties[i])
            db.session.add(qualification_round)

        db.session.commit()

    # login

    auth.login()

    # get qualification_rounds

    response = client.get(url)
    data = response.get_json()
    qualification_rounds = data["items"]

    for i, qualification_round in enumerate(qualification_rounds):
        assert qualification_round["name"] == qualification_rounds_properties[
            i]["name"]

    # get qualification_round that ends with "or 2"

    response = client.get(url + "?search=nd 2")
    data = response.get_json()
    qualification_rounds = data["items"]

    assert len(qualification_rounds) > 0

    for qualification_round in qualification_rounds:
        assert qualification_round["name"].find("nd 2") != -1


def test_create_qualification_round(app, client, auth):
    """creates qualification_round"""

    auth.login()

    # create qualification_round

    data = {"name": "test post qualification_round"}

    response = client.post(url, json=data)
    response_data = response.get_json()
    qualification_round_url = response_data["qualification_round"]

    response = client.get(qualification_round_url)
    response_data = response.get_json()

    with app.test_request_context():
        qualification_round = QualificationRound.get(response_data["id"])

        assert qualification_round is not None
        assert qualification_round.to_dict() == response_data


def test_delete_qualification_round(app, client, auth):
    """ create qualification_rounds and edit them"""

    # delete qualification_round
    auth.login()

    with app.app_context():
        qualification_round = QualificationRound(
            name="test qualification_round")
        db.session.add(qualification_round)
        db.session.commit()

        client.delete(url + f"/{qualification_round.id}")

        qualification_round = QualificationRound.get(qualification_round.id)

        assert qualification_round is None


def test_qualification_rounds_programs(app, client, auth):
    auth.login()

    with app.app_context():
        qualification_round = QualificationRound(
            name="test qualification_round")
        db.session.add(qualification_round)

        for i in range(10):

            program = Program(name=f"test program {i}")
            db.session.add(program)

            program.add_qualification_round(qualification_round)

        db.session.commit()

        response = client.get(url + f"/{qualification_round.id}/programs")
        qualification_round_programs = response.get_json()

        qualification_round_programs = qualification_round_programs["items"]

        programs = Program.query.limit(5).all()

        for i, program in enumerate(programs):
            assert qualification_round_programs[i]["name"] == program.name
