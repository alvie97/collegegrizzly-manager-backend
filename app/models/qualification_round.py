import flask
import app
from app.models.common import base_mixin, paginated_api_mixin, date_audit


class QualificationRound(app.db.Model, paginated_api_mixin.PaginatedAPIMixin,
                         base_mixin.BaseMixin, date_audit.DateAudit):
    """ Qualification Round model.

    Attributes:
         id (integer): model id.
         name (string): round name.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True, index=True)

    def __repr__(self):
        return f"<Qualification Round {self.name}>"

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "links": {
                "get_programs":
                flask.url_for("qualification_rounds.get_programs")
            }
        }
