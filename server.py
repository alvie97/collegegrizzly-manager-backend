from app import cli, create_app, db
from app.models.college import College
from app.models.college_details import CollegeDetails
from app.models.refresh_token import RefreshToken
from app.models.submission import Submission
from app.models.user import User
from app.models.major import Major
from app.models.detail import Detail

app = create_app()

# cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "College": College,
        "User": User,
        "RefreshToken": RefreshToken,
        "CollegeDetails": CollegeDetails,
        "Submission": Submission,
        "Major": Major,
        "Detail": Detail
    }
