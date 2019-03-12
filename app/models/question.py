import app
from app.models.common import base_mixin, paginated_api_mixin, date_audit


class Question(app.db.Model, base_mixin.BaseMixin,
               paginated_api_mixin.PaginatedAPIMixin, date_audit.DateAudit):
    """Question model.

    Attributes:
        id (integer): model id.
        name (string): question name.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True, index=True)

    def __repr__(self):
        return f"<Question {self.name}>"

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {"id": self.id, "name": self.name}
