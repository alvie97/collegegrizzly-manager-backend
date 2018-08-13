from flask import url_for
from datetime import datetime
from app import db, photos
from app.models.common import PaginatedAPIMixin
from app.models.state import State
from app.models.county import County
from app.models.place import Place
from app.models.consolidated_city import ConsolidatedCity
from app.models.major import Major
from app.models.relation_tables import (
    college_state, college_county, college_place, college_consolidated_city,
    college_major)
from hashlib import md5


class College(PaginatedAPIMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.String(50), unique=True)
  name = db.Column(db.String(256))
  room_and_board = db.Column(db.Numeric(8, 2), default=0)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow)
  type_of_institution = db.Column(db.String(256), nullable=True)
  phone = db.Column(db.String(256), nullable=True)
  website = db.Column(db.Text, nullable=True)
  in_state_tuition = db.Column(db.Numeric(8, 2), default=0)
  out_of_state_tuition = db.Column(db.Numeric(8, 2), default=0)
  location = db.Column(db.String(256), nullable=True)
  religious_affiliation = db.Column(db.String(256), nullable=True)
  setting = db.Column(db.String(256), nullable=True)
  number_of_students = db.Column(db.Integer, default=0)
  unweighted_hs_gpa = db.Column(db.Numeric(4, 2), default=0)
  sat = db.Column(db.Integer, default=0)
  act = db.Column(db.Integer, default=0)
  scholarships = db.relationship(
      "Scholarship",
      backref="college",
      cascade="all, delete-orphan",
      lazy="dynamic")

  pictures = db.relationship(
      "Picture",
      backref="college",
      cascade="all, delete-orphan",
      lazy="dynamic")

  majors = db.relationship(
      "Major",
      secondary=college_major,
      backref=db.backref("colleges", lazy="dynamic"))
  in_state_states = db.relationship(
      "State",
      secondary=college_state,
      backref=db.backref("colleges", lazy="dynamic"),
      lazy="dynamic")
  in_state_counties = db.relationship(
      "County",
      secondary=college_county,
      backref=db.backref("colleges", lazy="dynamic"),
      lazy="dynamic")
  in_state_places = db.relationship(
      "Place",
      secondary=college_place,
      backref=db.backref("colleges", lazy="dynamic"),
      lazy="dynamic")
  in_state_consolidated_cities = db.relationship(
      "ConsolidatedCity",
      secondary=college_consolidated_city,
      backref="colleges")

  ATTR_FIELDS = [
      "public_id", "name", "room_and_board", "created_at", "updated_at",
      "type_of_institution", "phone", "website", "in_state_tuition",
      "out_of_state_tuition", "location", "religious_affiliation", "setting",
      "number_of_students", "unweighted_hs_gpa", "sat", "act"
  ]

  def __repr__(self):
    return "<College {}>".format(self.name)

  # relationship methods
  def add_state(self, state):
    self.in_state_states.append(state)

  def add_county(self, county):
    self.in_state_county.append(county)

  def add_place(self, place):
    self.in_state_places.append(place)

  def add_consolidated_city(self, consolidated_city):
    self.in_state_consolidated_cities.append(consolidated_city)

  def add_major(self, major):
    self.majors.append(major)

  def remove_state(self, state):
    self.in_state_states.remove(state)

  def remove_county(self, county):
    self.in_state_county.remove(county)

  def remove_place(self, place):
    self.in_state_places.remove(place)

  def remove_consolidated_city(self, consolidated_city):
    self.in_state_consolidated_cities.remove(consolidated_city)

  def remove_major(self, major):
    self.majors.remove(major)

  def has_state(self, state_name=None, fips_code=None):
    if fips_code is not None:
      return self.in_state_states.filter(
          State.fips_code == fips_code).count() > 0
    else:
      return self.in_state_states.filter(State.name == state_name).count() > 0

  def has_county(self, county_name=None, fips_code=None):
    if fips_code is not None:
      return self.in_state_counties.filter(
          County.fips_code == fips_code).count() > 0
    else:
      return self.in_state_counties.filter(
          County.name == county_name).count() > 0

  def has_place(self, place_name=None, fips_code=None):
    if fips_code is not None:
      return self.in_state_places.filter(
          Place.fips_code == fips_code).count() > 0
    else:
      return self.in_place_name_place_names.filter(
          Place.name == place_name).count() > 0

  def has_consolidated_city(self, consolidated_city_name=None, fips_code=None):
    if fips_code is not None:
      return self.in_state_consolidated_cities.filter(
          ConsolidatedCity.fips_code == fips_code).count() > 0
    else:
      return self.in_state_consolidated_cities.filter(
          ConsolidatedCity.name == consolidated_city_name).count() > 0

  def has_major(self, major_name):
    return self.majors.filter(Major.name == major_name).count() > 0

  def get_avatar(self, size):
    digest = md5("test@email.com".encode("utf-8")).hexdigest()
    return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
        digest, size)

  def total_ofs(self):
    return self.room_and_board + self.out_of_state_tuition

  def total_is(self):
    return self.room_and_board + self.in_state_tuition

  def get_logo(self):
    logo = self.Pictures.filter_by(type="logo").first()

    if logo is None:
      return self.get_avatar(128)

    return photos.url(logo.name)

  def delete(self):
    """
            Scholarships doesn"t need to be removed manually
            because, the cascade option takes care of it
            """
    pics = self.Pictures.all()

    for pic in pics:
      pic.delete()

    db.session.delete(self)

  def to_dict(self):
    return {
        "public_id": self.public_id,
        "name": self.name,
        "room_and_board": str(self.room_and_board),
        "created_at": self.created_at.isoformat() + 'Z',
        "updated_at": self.updated_at.isoformat() + 'Z',
        "type_of_institution": self.type_of_institution,
        "phone": self.phone,
        "website": self.website,
        "in_state_tuition": str(self.in_state_tuition),
        "out_of_state_tuition": str(self.out_of_state_tuition),
        "location": self.location,
        "religious_affiliation": self.religious_affiliation,
        "setting": self.setting,
        "number_of_students": self.number_of_students,
        "unweighted_hs_gpa": str(self.unweighted_hs_gpa),
        "sat": self.sat,
        "act": self.act,
        "logo": self.get_logo(),
        "majors": self.majors,
        "in_state_requirement": {
            "state": self.in_state_states,
            "counties": self.in_state_counties,
            "places": self.in_state_places,
            "consolidated_cities": self.in_state_consolidated_cities
        },
        "_links": {
            "scholarships":
                url_for("scholarships", college_id=self.public_id),
            "pictures":
                url_for("pictures", college_id=self.public_id),
        }
    }

  def in_state_requirement():
    return {
        "state": self.in_state_states,
        "counties": self.in_state_counties,
        "places": self.in_state_places,
        "consolidated_cities": self.in_state_consolidated_cities
    }

  def from_dict(self, data):
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])
    self.updated_at = datetime.utcnow()
