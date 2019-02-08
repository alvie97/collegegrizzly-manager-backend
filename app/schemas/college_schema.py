from app.models.college import College
from marshmallow import (fields, Schema, validates, ValidationError, post_load)


class CollegeSchema(Schema):
    name = fields.String(
        required=True, error_messages={"required": "name required"})
    room_and_board = fields.Decimal(places=2)
    type_of_institution = fields.String(allow_none=True)
    phone = fields.String(allow_none=True)
    website = fields.String(allow_none=True)
    in_state_tuition = fields.Decimal(places=2)
    out_of_state_tuition = fields.Decimal(places=2)
    location = fields.String(allow_none=True)
    religious_affiliation = fields.String(allow_none=True)
    setting = fields.String(allow_none=True)
    number_of_students = fields.Integer()
    unweighted_hs_gpa = fields.Decimal(places=2)
    sat = fields.Integer()
    act = fields.Integer()

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

    @post_load
    def make_college(self, data):
        return College(**data)
