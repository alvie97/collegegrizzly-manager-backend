import marshmallow


class GradeSchema(marshmallow.Schema):
    """Grade schema

    Attributes:
        name (string): question name, required.
    """
    name = marshmallow.fields.String(
        required=True, error_messages={"required": "name required"})
    max = marshmallow.fields.Decimal(
        2, required=True, error_messages={"required": "max required"})
    min = marshmallow.fields.Decimal(
        2, required=True, error_messages={"required": "min required"})
    description = marshmallow.fields.String()
