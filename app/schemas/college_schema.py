from marshmallow import Schema, ValidationError, fields, post_load, validates

from app.models.college import College


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