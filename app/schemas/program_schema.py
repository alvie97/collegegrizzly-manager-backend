from marshmallow import Schema, fields, validates, ValidationError

class ProgramSchema(Schema):
    name = fields.String(required=True, error_messages={"required": "name is required"})
    round_qualification = fields.String()

    @validates("name")
    def validate_name(self, value):
        if len(value) > 256:
            raise ValidationError(
                "Name should not be longer than 256 characters")
