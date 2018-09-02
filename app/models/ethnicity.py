from .common.base_mixin import BaseMixin
from app import db

class Ethnicity(BaseMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(256), index=True, unique=True)

  ATTR_FIELDS = ["name"]

  def __repr__(self):
    return "<Ethnicity {}>".format(self.name)

  def to_dict(self):
    return {"name": self.name}
