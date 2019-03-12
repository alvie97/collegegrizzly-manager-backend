import app
import flask

from app.models.common import base_mixin
from app.models.common import date_audit
from app.models.common import paginated_api_mixin


class Major(app.db.Model, base_mixin.BaseMixin, date_audit.DateAudit,
            paginated_api_mixin.PaginatedAPIMixin):
    """Major model

    Attributes:
        id (integer): table id
        name (string): major name
        description (String): major description
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True, index=True)
    description = app.db.Column(app.db.Text, nullable=True)

    ATTR_FIELDS = ["name", "description"]

    def __repr__(self):
        return f"<major {self.name}>"

    def for_pagination(self):
        return {
            "id": self.id,
            "name": self.name,
            "links": {
                "get_major": flask.url_for("majors.get_major", id=self.id)
            }
        }

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "links": {
                "get_college": flask.url_for(
                    "majors.get_colleges", id=self.id),
            }
        }