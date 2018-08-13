from app import db


class Major(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(256), unique=True, index=True)
  description = db.Column(db.Text, nullable=True)

  ATTR_FIELDS = ["name", "description"]

  def __repr__(self):
    return "<Major {}>".format(self.name)

  def to_dict(self):
    return {"name": self.name, "description": self.description}

  def from_dict(self, data):
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])
