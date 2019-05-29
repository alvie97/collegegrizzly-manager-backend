#TODO: Add validation for password, email and username
import marshmallow
import re


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

        if len(value) < 4:
            raise marshmallow.ValidationError(
                "username must be at least 4 characters long")

        if re.match(r"/(?![.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])/",
                    value) is None:
            raise marshmallow.ValidationError("invalid username")

    @marshmallow.validates("email")
    def validate_email(self, value):
        if re.match(r"/^\S+@\S+$/", value) is None:
            raise marshmallow.ValidationError("invalid email")

    @marshmallow.validates("password")
    def validate_password(self, value):
        if len(value) < 8:
            raise marshmallow.ValidationError(
                "password must be at least 8 characters long")

        if re.search(r"/[A-Z]+/", value) is None:
            raise marshmallow.ValidationError(
                "password must at least 1 uppercase character")

        if re.search(r"/[0-9]+/", value) is None:
            raise marshmallow.ValidationError(
                "password must at least 1 number character")

        if re.search(r"/W/", value) is None:
            raise marshmallow.ValidationError(
                "password must have at least 1 special character")

        if re.search(r"/[a-z]+/", value) is None:
            raise marshmallow.ValidationError(
                "password must have at least 1 lowercase character")

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
