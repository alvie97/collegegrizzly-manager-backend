import marshmallow
from app.models import major


class MajorSchema(marshmallow.Schema):
    """Major schema

    Attributes:
        name (string): major name, required.
        description (string): major description
    """
    name = marshmallow.fields.String(
        required=True, error_messages={"required": "name required"})
    description = marshmallow.fields.String()
