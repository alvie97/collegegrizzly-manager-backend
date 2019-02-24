from flask import url_for

from app import db

from .common.base_mixin import BaseMixin
from .common.paginated_api_mixin import PaginatedAPIMixin


class State(db.Model, PaginatedAPIMixin, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    fips_code = db.Column(db.String(10), index=True, unique=True)
    __str_repr__ = "state"
    counties = db.relationship("County", backref="state", lazy="dynamic")
    places = db.relationship("Place", backref="state", lazy="dynamic")
    consolidated_cities = db.relationship(
        "ConsolidatedCity", backref="state", lazy="dynamic")

    ATTR_FIELDS = ["name", "fips_code"]

    def __repr__(self):
        return "<State {}>".format(self.name)

    def to_dict(self):
        return {
            "name": self.name,
            "fips_code": self.fips_code,
            "_links": {
                "counties":
                url_for(
                    "locations.get_state_counties", state_fips=self.fips_code),
                "places":
                url_for(
                    "locations.get_state_places", state_fips=self.fips_code),
                "consolidated_cities":
                url_for(
                    "locations.get_state_consolidated_cities",
                    state_fips=self.fips_code)
            }
        }

    def for_pagination(self):
        return self.to_dict()
