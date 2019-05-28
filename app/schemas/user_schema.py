#TODO: Add validation for password and email
import marshmallow


class UserSchema(marshmallow.Schema):
    """User schema"""

    username = marshmallow.fields.String(
        required=True, error_messages={"required": "username required"})
    first_name = marshmallow.fields.String(
        required=True, error_messages={"required": "first_name required"})
    last_name = marshmallow.fields.String(
        required=True, error_messages={"required": "last_name required"})
    email = marshmallow.fields.String(
        required=True, error_messages={"required": "email required"})
    password = marshmallow.fields.String(
        required=True, error_messages={"required": "password required"})
    role = marshmallow.fields.String(
        required=True, error_messages={"required": "role required"})

    @marshmallow.validates("username")
    def validate_username(self, value):
        if len(value) >= 120:
            raise marshmallow.ValidationError(
                "username must be shorter than 120 characters")

    @marshmallow.validates("first_name")
    def validate_first_name(self, value):
        if len(value) >= 256:
            raise marshmallow.ValidationError(
                "first_name must be shorter than 256 characters")

    @marshmallow.validates("last_name")
    def validate_last_name(self, value):
        if len(value) >= 256:
            raise marshmallow.ValidationError(
                "last_name must be shorter than 256 characters")
