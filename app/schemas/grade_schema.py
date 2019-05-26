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

    @marshmallow.validates("max")
    def validate_max(self, value):
        if value < 0:
            raise marshmallow.ValidationError(
                "grade max should be bigger or equal to 0")

    @marshmallow.validates("min")
    def validate_min(self, value):
        if value < 0:
            raise marshmallow.ValidationError(
                "grade min should be bigger or equal to 0")
