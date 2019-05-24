import app
import flask
from app.models.common import base_mixin, paginated_api_mixin, date_audit
from app.models import association_tables


class Option(app.db.Model, base_mixin.BaseMixin,
             paginated_api_mixin.PaginatedAPIMixin, date_audit.DateAudit):
    """
    Options for selection requirement.

    Attributes:
        id (integer): Model id.
        name (string): question name.
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True)

    str_repr = "option"

    def __repr__(self):
        return f"<Option {self.name}>"

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
            "links": {
                "get_option_questions":
                flask.url_for("options.get_questions", id=self.id)
            }
        }
