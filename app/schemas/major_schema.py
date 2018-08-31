from app.models.major import Major
from marshmallow import Schema, fields, validate, ValidationError, post_load

class MajorSchema(Schema):
  name = fields.String(required=True)
  description = fields.String()

  @validate("name")
  def validate_name(self, value):
    if len(value) > 256:
      raise ValidationError("Name should not be longer than 256 characters")

  @post_load
  def make_major(self, data):
    return Major(**data)
