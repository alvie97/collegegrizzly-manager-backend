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
      "Consolidated_city": ConsolidatedCity,
      "Major": Major,
      "Ethnicity": Ethnicity,
      "Program": Program
  }
