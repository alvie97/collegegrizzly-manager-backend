import marshmallow
from app.models import detail


class DetailSchema(marshmallow.Schema):
    name = marshmallow.fields.String(
        required=True, error_messages={"required": "name required"})
    value = marshmallow.fields.String(
        required=True, error_messages={"required": "value required"})
    type = marshmallow.fields.String(
        required=True, error_messages={"required": "type required"})

    @marshmallow.validates("type")
    def validate_type(self, value):
        if value not in ["string", "boolean", "decimal", "integer"]:
            raise marshmallow.ValidationError("type not allowed")
