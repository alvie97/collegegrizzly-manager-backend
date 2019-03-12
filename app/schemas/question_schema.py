import marshmallow


class QuestionSchema(marshmallow.Schema):
    """Question schema

    Attributes:
        name (string): question name, required.
    """
    name = marshmallow.fields.String(
        required=True, error_messages={"required": "name required"})
