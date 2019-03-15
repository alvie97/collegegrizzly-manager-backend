import app
from app.models.common import base_mixin, date_audit, paginated_api_mixin

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

program_requirement_qualification_round = app.db.Table(
    "program_requirement_qualification_round",
    app.db.Column("program_requirement_id", app.db.Integer,
                  app.db.ForeignKey("program_requirement.id")),
    app.db.Column("qualification_round_id", app.db.Integer,
                  app.db.ForeignKey("qualification_round.id")))


class ProgramRequirement(app.db.Model, base_mixin.BaseMixin,
                         date_audit.DateAudit,
                         paginated_api_mixin.PaginatedAPIMixin):
    """ Program requirement.

    Holds relationship between program and scholarship. Scholarship needs
    program.

    Attributes:
        id (integer): Model id.
        scholarship_id (integer): scholarship id.
        program_id (integer): program id.
        program (sqlalchemy.Model): program.
        qualification_rounds (sqlalchemy.relationship): qualification rounds
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    scholarship_id = app.db.Column(
        "scholarship_id",
        app.db.Integer,
        app.db.ForeignKey("scholarship.id"),
        nullable=False)
    program_id = app.db.Column(
        "program_id",
        app.db.Integer,
        app.db.ForeignKey("program.id"),
        nullable=False)
    program = app.db.relationship("Program")
    qualification_rounds = app.db.relationship(
        "QualificationRound",
        secondary=program_requirement_qualification_round,
        lazy="dynamic",
        backref=app.db.backref("programs_requirement", lazy="dynamic"))
