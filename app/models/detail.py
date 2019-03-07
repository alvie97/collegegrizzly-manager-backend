import app
import flask
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
    college_id = app.db.Column(
        app.db.Integer, app.db.ForeignKey("college.id"), nullable=True)
    str_repr = "detail"

    ATTR_FIELDS = ["value", "type"]

    def __repr__(self):
        return f"<Details {self.name}>"

    @staticmethod
    def validate_value(value, type):
        """validates if value is of certain type.

        Args:
            value (any): value to be checked.
            type (string): type of value.
        Returns:
            bool: True if value is of type, False otherwise.
        """

        if type not in ["integer", "boolean", "string", "decimal"]:
            return False

        try:
            if type == "integer":
                int(value)
            elif type == "boolean":
                if value not in ["yes", "no", "1", "0", "true", "false"]:
                    raise ValueError()
            elif type == "decimal":
                float(value)

            return True
        except ValueError:
            return False

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "type": self.type,
            "links": {
                "get_college": flask.url_for(
                    "details.get_college", id=self.id)
            }
        }
