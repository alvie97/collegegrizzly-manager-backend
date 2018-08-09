from datetime import datetime
from app import db
from app.models.common import PaginatedAPIMixin
from app.models.State import State
from app.models.County import County
from app.models.Place import Place
from app.models.Consolidated_city import Consolidated_city
from app.models.Ethnicity import Ethnicity
from app.models.Program import Program
from app.models.relation_tables import (
    scholarship_state, scholarship_county, scholarship_place,
    scholarship_consolidated_city, scholarship_program, scholarship_ethnicity,
    scholarships_needed)


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
      "Ethnicity", secondary=scholarship_ethnicity, backref="scholarships")
  programs = db.relationship(
      "Program", secondary=scholarship_program, backref="scholarships")
  scholarships_needed = db.relationship(
      "Scholarship",
      secondary=scholarships_needed,
      primaryjoin=(scholarships_needed.c.needs_id == id),
      secondaryjoin=(scholarships_needed.c.needed_id == id),
      backref="needed_by_scholarships")
  states = db.relationship(
      "State",
      secondary=scholarship_state,
      backref=db.backref("scholarships", lazy="dynamic"))
  counties = db.relationship(
      "County",
      secondary=scholarship_county,
      backref=db.backref("scholarships", lazy="dynamic"))
  places = db.relationship(
      "Place",
      secondary=scholarship_place,
      backref=db.backref("scholarships", lazy="dynamic"))
  consolidated_cities = db.relationship(
      "Consolidated_city",
      secondary=scholarship_consolidated_city,
      backref=db.backref("scholarships", lazy="dynamic"))

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
  def add_state(self, state):
    self.states.append(state)

  def add_county(self, county):
    self.counties.append(county)

  def add_place(self, place):
    self.places.append(place)

  def add_consolidated_city(self, consolidated_city):
    self.consolidated_cities.append(consolidated_city)

  def add_ethnicity(self, ethnicity):
    self.ethnicities.append(ethnicity)

  def add_program(self, progam):
    self.programs.append(progam)

  def remove_state(self, state):
    self.states.remove(state)

  def remove_county(self, county):
    self.counties.remove(county)

  def remove_place(self, place):
    self.places.remove(place)

  def remove_consolidated_city(self, consolidated_city):
    self.consolidated_cities.remove(consolidated_city)

  def remove_ethnicity(self, ethnicity):
    self.ethnicities.remove(ethnicity)

  def remove_program(self, progam):
    self.programs.remove(progam)

  def has_state(self, state_name, fips_code=None):
    if fips_code is not None:
      return self.states.filter(State.fips_code == fips_code).count() > 0
    else:
      return self.states.filter(State.name == state_name).count() > 0

  def has_county(self, county_name, fips_code=None):
    if fips_code is not None:
      return self.counties.filter(County.fips_code == fips_code).count() > 0
    else:
      return self.counties.filter(County.name == county_name).count() > 0

  def has_place(self, place_name, fips_code=None):
    if fips_code is not None:
      return self.places.filter(Place.fips_code == fips_code).count() > 0
    else:
      return self.in_place_name_place_names.filter(
          Place.name == place_name).count() > 0

  def has_consolidated_city(self, consolidated_city_name, fips_code=None):
    if fips_code is not None:
      return self.consolidated_cities.filter(
          Consolidated_city.fips_code == fips_code).count() > 0
    else:
      return self.consolidated_cities.filter(
          Consolidated_city.name == consolidated_city_name).count() > 0

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
            self.unweighted_hs_gpa,
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
            self.programs,
        "ethnicities":
            self.ethnicities,
        "location_requirement": {
            "states": self.states,
            "counties": self.counties,
            "places": self.places,
            "consolidated_cities": self.consolidated_cities
        }
    }

  def from_dict(self, data):
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])
    self.updated_at = datetime.utcnow()
