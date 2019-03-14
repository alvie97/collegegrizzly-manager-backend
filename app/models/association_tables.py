import app

college_major = app.db.Table(
    "college_major",
    app.db.Column("college_id", app.db.Integer,
                  app.db.ForeignKey("college.id")),
    app.db.Column("major_id", app.db.Integer, app.db.ForeignKey("major.id")))

program_qualification_round = app.db.Table(
    "program_qualification_round",
    app.db.Column("program_id", app.db.Integer,
                  app.db.ForeignKey("program.id")),
    app.db.Column("qualification_round_id", app.db.Integer,
                  app.db.ForeignKey("qualification_round.id")))

scholarships_needed = app.db.Table(
    "scholarships_needed",
    app.db.Column("needs_id", app.db.Integer,
                  app.db.ForeignKey("scholarship.id")),
    app.db.Column("needed_id", app.db.Integer,
                  app.db.ForeignKey("scholarship.id")))
