from app.common.utils import generate_public_id
from app.models.scholarship import Scholarship
from marshmallow import fields, Schema, validates, ValidationError, post_load


class ScholarshipSchema(Schema):
    name = fields.String(
        required=True, error_messages={"required": "Name is required"})
    sat = fields.Integer()
    act = fields.Integer()
    amount = fields.String()
    amount_expression = fields.String()
    unweighted_hs_gpa = fields.Decimal(places=2)
    class_rank = fields.Integer()
    legal_status = fields.String()
    relevant_information = fields.String()
    graduated_spring_before_scholarship = fields.Boolean()
    paid_full_time_christian_ministry_parent = fields.Boolean()
    parents_higher_education = fields.Boolean()
    siblings_currently_in_scholarship = fields.Boolean()
    application_needed = fields.Boolean()
    first_choice_national_merit = fields.String()
    exclude_from_match = fields.Boolean()
    group_by = fields.Integer()
    first_generation_higher_education = fields.Boolean()
    type = fields.String()
    description = fields.String()

    @validates("name")
    def validate_name(self, value):
        if len(value) > 256:
            raise ValidationError(
                "Name should not be longer than 256 characters")

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

    @validates("amount_expression")
    def validate_amount_expression(self, value):
        pass

    @validates("class_rank")
    def validate_class_rank(self, value):
        if 1 < value > 100:
            raise ValidationError("class rank must be between 1 and 100")

