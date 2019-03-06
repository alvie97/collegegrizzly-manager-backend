import app
from app.models.common import paginated_api_mixin
from app.models.common import base_mixin


class Detail(app.db.Model, paginated_api_mixin.PaginatedAPIMixin,
             base_mixin.BaseMixin):
    """Detail model.

    Attributes:
        id (integer): row id.
        name (string): name of the detail.
        value (string): value of the detail.
        type (string): detail type boolean, integer, decimal or string.
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256))
    value = app.db.Column(app.db.Text)
    type = app.db.Column(app.db.String(256))
    college_details_id = app.db.Column(
        app.db.Integer, app.db.ForeignKey("college_details.id"), nullable=True)
    str_repr = "detail"

    ATTR_FIELDS = ["value", "type"]

    def __repr__(self):
        return f"<Details {self.name}>"

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "type": self.type
        }
