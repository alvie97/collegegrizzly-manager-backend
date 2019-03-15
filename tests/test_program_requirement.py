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
