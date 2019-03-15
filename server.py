from app import cli, create_app, db
from app.models.college import College
from app.models.scholarship import Scholarship
from app.models.qualification_round import QualificationRound
from app.models.grade import Grade
from app.models.program import Program
from app.models.question import Question
from app.models.college_details import CollegeDetails
from app.models.refresh_token import RefreshToken
from app.models.submission import Submission
from app.models.user import User
from app.models.major import Major
from app.models.detail import Detail
from app.models.association_tables import ProgramRequirement

app = create_app()

# cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "College": College,
        "Scholarship": Scholarship,
        "User": User,
        "RefreshToken": RefreshToken,
        "CollegeDetails": CollegeDetails,
        "Submission": Submission,
        "Major": Major,
        "Detail": Detail,
        "Question": Question,
        "Program": Program,
        "QualificationRound": QualificationRound,
        "ProgramRequirement": ProgramRequirement,
        "Grade": Grade
    }
