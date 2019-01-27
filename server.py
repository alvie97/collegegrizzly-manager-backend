from app import create_app

app = create_app()

from app import cli, db
from app.models.user import User
from app.models.college import College
from app.models.scholarship import Scholarship
from app.models.major import Major
from app.models.program import Program
from app.models.state import State
from app.models.county import County
from app.models.place import Place
from app.models.consolidated_city import ConsolidatedCity
from app.models.refresh_token import RefreshToken
from app.models.college_details import CollegeDetails
from app.models.scholarship_details import ScholarshipDetails

cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "College": College,
        "Scholarship": Scholarship,
        "State": State,
        "County": County,
        "Place": Place,
        "Consolidated_city": ConsolidatedCity,
        "Major": Major,
        "Program": Program,
        "User": User,
        "RefreshToken": RefreshToken,
        "CollegeDetails": CollegeDetails,
        "ScholarshipDetails": ScholarshipDetails
    }
