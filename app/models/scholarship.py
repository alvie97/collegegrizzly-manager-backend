from datetime import datetime

from app import db
from app.models.common import PaginatedAPIMixin
from app.models.consolidated_city import ConsolidatedCity
from app.models.county import County
from app.models.ethnicity import Ethnicity
from app.models.place import Place
from app.models.program import Program
from app.models.relation_tables import (
    scholarship_consolidated_city, scholarship_county, scholarship_ethnicity,
    scholarship_place, scholarship_program, scholarship_state,
    scholarships_needed)
from app.models.state import State


class Scholarship(PaginatedAPIMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.String(50), unique=True)
  name = db.Column(db.String(256))
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow)
  college_id = db.Column(db.Integer, db.ForeignKey('college.id'))
  act = db.Column(db.SmallInteger, default=0)
  sat = db.Column(db.SmallInteger, default=0)
  amount = db.Column(db.String(256), nullable=True)
  amount_expression = db.Column(db.String(256), nullable=True)
  unweighted_hs_gpa = db.Column(db.Numeric(3, 2), default=0)
  class_rank = db.Column(db.Integer, nullable=True)
  legal_status = db.Column(db.String(256), nullable=True)
  relevant_information = db.Column(db.String(256), nullable=True)
  graduated_spring_before_scholarship = db.Column(db.Boolean, default=False)
  paid_full_time_christian_ministry_parent = db.Column(
      db.Boolean, default=False)
  parents_higher_education = db.Column(db.Boolean, default=False)
  siblings_currently_in_scholarship = db.Column(db.Boolean, default=False)
  application_needed = db.Column(db.Boolean, default=False)
  first_choice_national_merit = db.Column(db.String(256), nullable=True)
  exclude_from_match = db.Column(db.Boolean, default=False)
  group_by = db.Column(db.Integer, nullable=True)
  first_generation_highed_education = db.Column(db.Boolean, default=False)
  type = db.Column(db.String(256))
  description = db.Column(db.Text)
  ethnicities = db.relationship(
      "Ethnicity",
      secondary=scholarship_ethnicity,
      backref=db.backref("scholarships", lazy="dynamic"))
  programs = db.relationship(
      "Program",
      secondary=scholarship_program,
      backref=db.backref("scholarships", lazy="dynamic"),
      lazy="dynamic")
  scholarships_needed = db.relationship(
      "Scholarship",
      secondary=scholarships_needed,
      primaryjoin=(scholarships_needed.c.needs_id == id),
      secondaryjoin=(scholarships_needed.c.needed_id == id),
      backref=db.backref("needed_by_scholarships", lazy="dynamic"),
      lazy="dynamic")
  states = db.relationship(
      "State",
      secondary=scholarship_state,
      backref=db.backref("scholarships", lazy="dynamic"),
      lazy="dynamic")
  counties = db.relationship(
      "County",
      secondary=scholarship_county,
      backref=db.backref("scholarships", lazy="dynamic"),
      lazy="dynamic")
  places = db.relationship(
      "Place",
      secondary=scholarship_place,
      backref=db.backref("scholarships", lazy="dynamic"),
      lazy="dynamic")
  consolidated_cities = db.relationship(
      "ConsolidatedCity",
      secondary=scholarship_consolidated_city,
      backref=db.backref("scholarships", lazy="dynamic"),
      lazy="dynamic")

  ATTR_FIELDS = [
      "name", "act", "sat", "amount", "amount_expression", "unweighted_hs_gpa",
      "class_rank", "legal_status", "relevant_information",
      "graduated_spring_before_scholarship",
      "paid_full_time_christian_ministry_parent", "parents_higher_education",
      "siblings_currently_in_scholarship", "application_needed",
      "first_choice_national_merit", "exclude_from_match", "group_by",
      "first_generation_highed_education", "type", "description"
  ]

  def __repr__(self):
    return '<Scholarship {}>'.format(self.name)

  # relationships methods
  def get_location_entity_query(self, location_obj):
    if isinstance(location_obj, State):
      location_query = self.states
      location_entity = State
    elif isinstance(location_obj, County):
      location_query = self.counties
      location_entity = County
    elif isinstance(location_obj, Place):
      location_query = self.places
      location_entity = Place
    elif isinstance(location_obj, ConsolidatedCity):
      location_query = self.consolidated_cities
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
      location_query = self.states
    elif location_entity is County:
      location_query = self.counties
    elif location_entity is Place:
      location_query = self.places
    elif location_entity is ConsolidatedCity:
      location_query = self.consolidated_cities
    else:
      return None

    return location_query.filter(
        location_entity.fips_code == fips_code).count() > 0

  def add_ethnicity(self, ethnicity):
    self.ethnicities.append(ethnicity)

  def add_program(self, program):
    if not self.has_program(program.name):
      self.programs.append(program)
      return True
    return False

  def remove_ethnicity(self, ethnicity):
    self.ethnicities.remove(ethnicity)

  def remove_program(self, program):
    if self.has_program(program.name):
      self.programs.remove(program)
      return True
    return False

  def has_ethnicity(self, ethnicity_name):
    return self.ethnicities.filter(
        Ethnicity.name == ethnicity_name).count() > 0

  def has_program(self, program_name):
    return self.programs.filter(Program.name == program_name).count() > 0

  def needs_scholarship(self, scholarship):
    if not self.needs(scholarship):
      self.scholarships_needed.append(scholarship)

  def remove_needed_scholarship(self, scholarship):
    if self.needs(scholarship):
      self.scholarships_needed.remove(scholarship)

  def needs(self, scholarship):
    return self.scholarships_needed.filter(
        scholarships_needed.c.needed_id == scholarship.id).count() > 0

  def get_programs(self):
    return [program.to_dict() for program in self.programs.all()]

  def get_location_requirement(self, location_entity, page, per_page):

    if location_entity is State:
      location_name = "states"
      location_query = self.states
      location_url = "scholarship_location_requirement_states"
    elif location_entity is County:
      location_name = "counties"
      location_query = self.counties
      location_url = "scholarship_location_requirement_counties"
    elif location_entity is Place:
      location_name = "places"
      location_query = self.places
      location_url = "scholarship_location_requirement_places"
    else:
      location_name = "consolidated_cities"
      location_query = self.consolidated_cities
      location_url = "scholarship_location_requirement_consolidated_cities"

    return {
        location_name:
            self.to_collection_dict(
                location_query,
                page,
                per_page,
                location_url,
                scholarship_id=self.public_id)
    }

  def location_requirements(self):
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
        "public_id":
            self.public_id,
        "name":
            self.name,
        "created_at":
            self.created_at.isoformat() + 'Z',
        "updated_at":
            self.updated_at.isoformat() + 'Z',
        "act":
            self.act,
        "sat":
            self.sat,
        "amount":
            self.amount,
        "amount_expression":
            self.amount_expression,
        "unweighted_hs_gpa":
            str(self.unweighted_hs_gpa),
        "class_rank":
            self.class_rank,
        "legal_status":
            self.legal_status,
        "relevant_information":
            self.relevant_information,
        "graduated_spring_before_scholarship":
            self.graduated_spring_before_scholarship,
        "paid_full_time_christian_ministry_parent":
            self.paid_full_time_christian_ministry_parent,
        "parents_higher_education":
            self.parents_higher_education,
        "siblings_currently_in_scholarship":
            self.siblings_currently_in_scholarship,
        "application_needed":
            self.application_needed,
        "first_choice_national_merit":
            self.first_choice_national_merit,
        "exclude_from_match":
            self.exclude_from_match,
        "group_by":
            self.group_by,
        "first_generation_highed_education":
            self.first_generation_highed_education,
        "type":
            self.type,
        "description":
            self.description,
        "programs":
            self.get_programs(),
        # "ethnicities":
        #     self.ethnicities,
        "location_requirement":
            self.location_requirements()
    }

  def from_dict(self, data):
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])
    self.updated_at = datetime.utcnow()
