import app
import flask
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

    def __repr__(self):
        return f"<ProgramRequirement {self.program.name} " \
            f"for scholarship {self.scholarship_id}>"

    def has_qualification_round(self, qualification_round):
        """Checks if program requirement has qualification round.

        Args:
            qualification_round (QualificationRound): qualification round.

        Returns:
            bool: True if program has qualification round, false otherwise.
        """
        return self.qualification_rounds.filter_by(
            id=qualification_round.id).count() > 0

    def add_qualification_round(self, qualification_round):
        """Adds qualification round to program requirement.

        Args:
            qualification_round (QualificationRound): qualification round
        """
        if not self.has_qualification_round(qualification_round):
            self.qualification_rounds.append(qualification_round)

    def remove_qualification_round(self, qualification_round):
        """Removes qualification round from program requirement.

        Args:
            qualification_round (QualificationRound): qualification round
        """
        if self.has_qualification_round(qualification_round):
            self.qualification_rounds.remove(qualification_round)

    def to_dict(self):
        return {
            "id": self.id,
            "links": {
                "get_program":
                flask.url_for("programs.get_program", id=self.program_id),
                "get_qualification_rounds":
                flask.url_for(
                    "scholarships.get_program_requirement_qualification_rounds",
                    scholarship_id=self.scholarship_id,
                    program_id=self.program_id)
            }
        }
