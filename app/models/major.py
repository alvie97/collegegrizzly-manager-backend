from .common import PaginatedAPIMixin, BaseMixin
from app import db

class Major(db.Model, PaginatedAPIMixin, BaseMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(256), unique=True, index=True)
  description = db.Column(db.Text, nullable=True)

  ATTR_FIELDS = ["name", "description"]

  def __repr__(self):
    return "<Major {}>".format(self.name)

  def to_dict(self):
    return {"name": self.name, "description": self.description}
