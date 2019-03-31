import app
from app.models.common import base_mixin, paginated_api_mixin, date_audit


class Option(app.db.Model, base_mixin.BaseMixin,
             paginated_api_mixin.PaginatedAPIMixin, date_audit.DateAudit):
    """
    Options for selection requirement.

    Attributes:
        id (integer): Model id.
        name (string): question name.
        description (string): description.
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True)
    description = app.db.Column(app.db.Text, nullable=True)

    def __repr__(self):
        return f"<Option {self.name}>"

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
