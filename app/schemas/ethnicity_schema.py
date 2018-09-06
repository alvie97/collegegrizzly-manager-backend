from marshmallow import ValidationError, validates, Schema, fields

class EthnicitySchema(Schema):
    name = fields.String(required=True, error_messages={"required": "name is required"})

    @validates("name")
    def validate_name(self, value):
        if len(value) > 256:
            raise ValidationError(
                "Name should not be longer than 256 characters")
