from .common.base_mixin import BaseMixin
from .common.paginated_api_mixin import PaginatedAPIMixin
from app import db


class Place(db.Model, BaseMixin, PaginatedAPIMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(256))
  fips_code = db.Column(db.String(10), index=True, unique=True)
  state_id = db.Column(db.Integer, db.ForeignKey("state.id"))

  ATTR_FIELDS = ["name", "fips_code"]

  def __repr__(self):
    return "<Place (city/town) {}>".format(self.name)

  def for_pagination(self):
    return self.to_dict()

  def to_dict(self):
    return {
        "name": self.name,
        "fips_code": self.fips_code,
        "state": self.state.name
    }
