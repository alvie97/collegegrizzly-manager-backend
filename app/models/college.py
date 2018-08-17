from datetime import datetime
from hashlib import md5

from flask import url_for

from app import db, photos
from app.models.common import PaginatedAPIMixin
from app.models.consolidated_city import ConsolidatedCity
from app.models.county import County
from app.models.major import Major
from app.models.place import Place
from app.models.relation_tables import (college_consolidated_city,
                                        college_county, college_major,
                                        college_place, college_state)
from app.models.state import State


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
      backref=db.backref("colleges", lazy="dynamic"),
      lazy="dynamic")
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
      backref=db.backref("colleges", lazy="dynamic"),
      lazy="dynamic")

  ATTR_FIELDS = [
      "public_id", "name", "room_and_board", "created_at", "updated_at",
      "type_of_institution", "phone", "website", "in_state_tuition",
      "out_of_state_tuition", "location", "religious_affiliation", "setting",
      "number_of_students", "unweighted_hs_gpa", "sat", "act"
  ]

  def __repr__(self):
    return "<College {}>".format(self.name)

  # relationship methods
  def add_major(self, major):
    if not self.has_major(major.name):
      self.majors.append(major)
      return True
    return False

  def remove_major(self, major):
    if self.has_major(major.name):
      self.majors.remove(major)
      return True
    return False

  def get_location_entity_query(self, location_obj):
    if isinstance(location_obj, State):
      location_query = self.in_state_states
      location_entity = State
    elif isinstance(location_obj, County):
      location_query = self.in_state_counties
      location_entity = County
    elif isinstance(location_obj, Place):
      location_query = self.in_state_places
      location_entity = Place
    elif isinstance(location_obj, ConsolidatedCity):
      location_query = self.in_state_consolidated_cities
      location_entity = ConsolidatedCity
    else:
      return None

    return location_entity, location_query

  def add_location(self, location_obj):
    instance = self.get_location_entity_query(location_obj)
    if instance is None:
      return False

    location_entity, location_query = instance

    if not self.has_location(location_entity, location_obj.fips_code):
      location_query.append(location_obj)
      return True
    return False

  def remove_location(self, location_obj):
    instance = self.get_location_entity_query(location_obj)
    if instance is None:
      return False

    location_entity, location_query = instance

    if self.has_location(location_entity, location_obj.fips_code):
      location_query.remove(location_obj)
      return True
    return False

  def has_location(self, location_entity, fips_code):
    if location_entity is State:
      location_query = self.in_state_states
    elif location_entity is County:
      location_query = self.in_state_counties
    elif location_entity is Place:
      location_query = self.in_state_places
    elif location_entity is ConsolidatedCity:
      location_query = self.in_state_consolidated_cities
    else:
      return None

    return location_query.filter(
        location_entity.fips_code == fips_code).count() > 0

  def has_major(self, major_name):
    return self.majors.filter(Major.name == major_name).count() > 0

  def get_location_requirement(self, location_entity, page, per_page):

    if location_entity is State:
      location_name = "states"
      location_query = self.in_state_states
      location_url = "college_in_state_requirement_states"
    elif location_entity is County:
      location_name = "counties"
      location_query = self.in_state_counties
      location_url = "college_in_state_requirement_counties"
    elif location_entity is Place:
      location_name = "places"
      location_query = self.in_state_places
      location_url = "college_in_state_requirement_places"
    elif location_entity is ConsolidatedCity:
      location_name = "consolidated_cities"
      location_query = self.in_state_consolidated_cities
      location_url = "college_in_state_requirement_consolidated_cities"
    else:
      return {"error": "Entity not a location"}

    return {
        location_name:
            self.to_collection_dict(
                location_query,
                page,
                per_page,
                location_url,
                college_id=self.public_id)
    }

  def get_majors(self):

    return [major.to_dict() for major in self.majors.all()]

  def get_avatar(self, size):
    digest = md5("test@email.com".encode("utf-8")).hexdigest()
    return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
        digest, size)

  def total_ofs(self):
    return self.room_and_board + self.out_of_state_tuition

  def total_is(self):
    return self.room_and_board + self.in_state_tuition

  def get_logo(self):
    logo = self.pictures.filter_by(type="logo").first()

    if logo is None:
      return self.get_avatar(128)

    return photos.url(logo.name)

  def delete(self):
    """
            Scholarships don't need to be removed manually
            because, the cascade option takes care of it
            """
    pics = self.pictures.all()

    for pic in pics:
      pic.delete()

    db.session.delete(self)

  def in_state_requirement(self):
    return {
        "state":
            self.get_location_requirement(State, 1, 15),
        "counties":
            self.get_location_requirement(County, 1, 15),
        "places":
            self.get_location_requirement(Place, 1, 15),
        "consolidated_cities":
            self.get_location_requirement(ConsolidatedCity, 1, 15)
    }

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
        "majors": self.get_majors(),
        "_links": {
            "scholarships":
                url_for("scholarships", college_id=self.public_id),
            "pictures":
                url_for("pictures", college_id=self.public_id),
            "in_state_requirement":
                self.in_state_requirement()
        }
    }

  def from_dict(self, data):
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])
    self.updated_at = datetime.utcnow()
