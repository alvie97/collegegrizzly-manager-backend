import marshmallow


class QualificationRoundSchema(marshmallow.Schema):
    """Qualification Round schema.

    Attributes:
        name (string): program name, required.
    """
    name = marshmallow.fields.String(
        required=True, error_messages={"required": "name required"})
