import re

from marshmallow import Schema, ValidationError, fields, validates


class ScholarshipSchema(Schema):
    name = fields.String(
        required=True, error_messages={"required": "name field is required"})
    amount = fields.String(
        required=True, error_messages={"required": "amount field is required"})
    amount_expression = fields.String(allow_none=True)
    application_needed = fields.Boolean()
    exclude_from_match = fields.Boolean()
    group = fields.Integer(allow_none=True)
    type = fields.String(allow_none=True)
    description = fields.String(allow_none=True)

    @validates("amount_expression")
    def validate_amount_expression(self, value):
        components = value.split('+')

        for component in components:

            AMOUNT_REGEX = ""

            if component[0] == '$':
                AMOUNT_REGEX = "\([0-9]+\)"
            elif component[0] == '%':
                AMOUNT_REGEX = "\((([0-9]+-[0-9]+))\)\[(t|r)\]"
            else:
                raise ValidationError(
                    "incorrect amount type must specify amount ($) or range (%)"
                )

            compiled_regex = re.compile(AMOUNT_REGEX)

            if compiled_regex.match(component[1:]) is None:
                raise ValidationError("Incorrent amount expression")
