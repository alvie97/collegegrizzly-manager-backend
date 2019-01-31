from app.common.utils import generate_public_id
from app.models.user import User
from marshmallow import (fields, Schema, validates, ValidationError, post_load)
from security.utils import ADMINISTRATOR, MODERATOR, BASIC


class CollegeSchema(Schema):
    #TODO: add validation for username, email and password
    username = fields.String(120, required=True)
    email = fields.String(120, required=True)
    role = fields.String(256, required=True)

    @validates("role")
    def validate_role(self, value):
        if value not in [ADMINISTRATOR, MODERATOR, BASIC]:
            raise ValidationError("role doesn't exist")

    @post_load
    def make_user(self, data):
        return User(public_id=generate_public_id(), **data)
