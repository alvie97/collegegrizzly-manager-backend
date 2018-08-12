from app import create_app, db, cli
from app.models.College import College
from app.models.Scholarship import Scholarship
from app.models.State import State
from app.models.County import County
from app.models.Place import Place
from app.models.Consolidated_city import Consolidated_city
from app.models.Ethnicity import Ethnicity
from app.models.Major import Major
from app.models.Program import Program

app = create_app()
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
      "Consolidated_city": Consolidated_city,
      "Major": Major,
      "Ethnicity": Ethnicity,
      "Program": Program
  }
