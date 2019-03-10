import app
from app.models.common import base_mixin, paginated_api_mixin, date_audit
from app.models import association_tables


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

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {"id": self.id, "name": self.name, "links": {}}
