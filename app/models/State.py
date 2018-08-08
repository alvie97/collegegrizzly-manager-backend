from app import db
from app.models.County import County
from app.models.Place import Place
from app.models.Consolidated_city import Consolidated_city


class State(db.model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(256))
  fips_code = db.Column(db.String(10), index=True, unique=True)
  counties = db.relationship("counties", backref="state", lazy="dynamic")
  places = db.relationship("places", backref="state", lazy="dynamic")
  consolidated_cities = db.relationship(
      "consolidated_cities", backref="state", lazy="dynamic")

  ATTR_FIELDS = ["name", "fips_code"]

  def __repr__(self):
    return "<State {}>".format(self.name)

  def to_dict(self):
    return {"name": self.name, "fips_code": self.fips_code}

  def from_dict(self, data):
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])
