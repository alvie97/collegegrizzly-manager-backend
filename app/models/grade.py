import app
from app.models.common import base_mixin, date_audit, paginated_api_mixin

class Grade(app.db.Model, base_mixin.BaseMixin, date_audit.DateAudit, paginated_api_mixin.PaginatedAPIMixin):
    """Grade model.

    Attributes:
        id (integer): model id.
        name (string): grade name.
        max (Decimal): maximum grade value.
        min (Decimal): minimum grade value.
        description (string): grade description.
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True, index=True)
    max = app.db.Column(app.db.Numeric(8, 2))
    min = app.db.Column(app.db.Numeric(8, 2))
    description = app.db.Column(app.db.String(256), nullable=True)
    str_repr = "grade"

    ATTR_FIELDS = ["name", "max", "min", "description"]

    def __repr__(self):
        return f"<Grade {self.name}>"

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.id,
            "max": self.max,
            "min": self.min,
            "description": self.description
        }
