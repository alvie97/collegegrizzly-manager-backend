from marshmallow import fields, Schema, validates, ValidationError
import re


class ScholarshipSchema(Schema):
    name = fields.String(required=True,
                         error_messages={"required": "name field is required"})
    sat = fields.Integer()
    act = fields.Integer()
    amount = fields.String(allow_none=True)
    amount_expression = fields.String(allow_none=True)
    unweighted_hs_gpa = fields.Decimal(places=2)
    class_rank = fields.Integer(allow_none=True)
    legal_status = fields.String(allow_none=True)
    relevant_information = fields.String(allow_none=True)
    graduated_spring_before_scholarship = fields.Boolean()
    paid_full_time_christian_ministry_parent = fields.Boolean()
    parents_higher_education = fields.Boolean()
    siblings_currently_in_scholarship = fields.Boolean()
    application_needed = fields.Boolean()
    first_choice_national_merit = fields.Boolean()
    exclude_from_match = fields.Boolean()
    group_by = fields.Integer(allow_none=True)
    first_generation_higher_education = fields.Boolean()
    type = fields.String(allow_none=True)
    description = fields.String(allow_none=True)

    @validates("name")
    def validate_name(self, value):
        if len(value) > 256:
            raise ValidationError(
                "Name should not be longer than 256 characters")

    @validates("group_by")
    def validate_group_by(self, value):
        if value and value < 1:
            raise ValidationError("value should be positive")

    @validates("unweighted_hs_gpa")
    def validate_unweighted_hs_gpa(self, value):
        if 0 < value > 4.0:
            raise ValidationError("Unweighted high school GPA "
                                  "must be between 0 and 4.0")

    @validates("sat")
    def validate_sat(self, value):
        if 0 < value > 1600:
            raise ValidationError("SAT score must be between 0 and 1600")

    @validates("act")
    def validate_act(self, value):
        if 0 < value > 36:
            raise ValidationError("ACT score must be between 0 and 36")

    @validates("class_rank")
    def validate_class_rank(self, value):
        if value and 1 < value > 100:
            raise ValidationError("class rank must be between 1 and 100")

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
                raise ValidationError("incorrect amount type must specify amount ($) or range (%)")

            compiled_regex = re.compile(AMOUNT_REGEX)

            if compiled_regex.match(component[1:]) is None:
                raise ValidationError("Incorrent amount expression")
