import app
import flask
from app.models.common import base_mixin, paginated_api_mixin, date_audit
from app.models import association_tables
from app.models import qualification_round as qualification_round_model


class Program(app.db.Model, paginated_api_mixin.PaginatedAPIMixin,
              base_mixin.BaseMixin, date_audit.DateAudit):
    """ Program model.
    
    Attributes:
         id (integer): model id.
         name (string): program name.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True, index=True)
    description = app.db.Column(app.db.Text, nullable=True)
    qualification_rounds = app.db.relationship(
        "QualificationRound",
        secondary=association_tables.program_qualification_round,
        lazy="dynamic",
        backref=app.db.backref("programs", lazy="dynamic"))

    ATTR_FIELDS = ["name", "description"]

    def __repr__(self):
        return f"<Program {self.name}>"

    def has_qualification_round(self, qualification_round_id):
        """checks if program has qualification_round.

        Args:
            self (class): program class.
            qualification_round_id (integer): qualification_round id.
        Returns:
            Boolean: true if program has qualification_round, false otherwise.

        """
        return self.qualification_rounds.filter(
            qualification_round_model.QualificationRound.id ==
            qualification_round_id).count() > 0

    def add_qualification_round(self, qualification_round):
        """Adds qualification_round to program.

        Args:
            self (class): program class.
            qualification_round (sqlalchemy.Model): qualification_round object.
        """
        if not self.has_qualification_round(qualification_round.id):
            self.qualification_rounds.append(qualification_round)

    def remove_qualification_round(self, qualification_round):
        """Removes qualification_round to program.

        Args:
            self (class): program class.
            qualification_round (sqlalchemy.Model): qualification_round object.
        """
        if self.has_qualification_round(qualification_round.id):
            self.qualification_rounds.remove(qualification_round)

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "links": {
                "get_qualification_rounds": flask.url_for("programs.get_qualification_rounds", id=self.id)
            }
        }
