import marshmallow


class ProgramSchema(marshmallow.Schema):
    """Program schema.

    Attributes:
        name (string): program name, required.
        description (string): program description.
    """
    name = marshmallow.fields.String(
        required=True, error_messages={"required": "name required"})
    description = marshmallow.fields.String()
