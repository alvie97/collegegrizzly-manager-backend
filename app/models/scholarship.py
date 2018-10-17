from .common.base_mixin import BaseMixin
from .common.date_audit import DateAudit
from .common.location_mixin import LocationMixin
from .common.location_blacklist_mixin import LocationBlacklistMixin
from .common.paginated_api_mixin import PaginatedAPIMixin
from .ethnicity import Ethnicity
from .program import Program
from .relationship_tables import (scholarship_ethnicity, scholarship_program,
                                  scholarships_needed)

from app import db
from flask import url_for


# TODO: add common interface for add_, remove_, has_... models
class Scholarship(PaginatedAPIMixin, LocationMixin, LocationBlacklistMixin,
                  DateAudit, BaseMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.String(50), unique=True)
  name = db.Column(db.String(256))
  college_id = db.Column(db.Integer, db.ForeignKey("college.id"))
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
  first_generation_higher_education = db.Column(db.Boolean, default=False)
  type = db.Column(db.String(256))
  description = db.Column(db.Text)
  ethnicities = db.relationship(
      "Ethnicity",
      secondary=scholarship_ethnicity,
      backref=db.backref("scholarships", lazy="dynamic"),
      lazy="dynamic")
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

  ATTR_FIELDS = [
      "name", "act", "sat", "amount", "amount_expression", "unweighted_hs_gpa",
      "class_rank", "legal_status", "relevant_information",
      "graduated_spring_before_scholarship",
      "paid_full_time_christian_ministry_parent", "parents_higher_education",
      "siblings_currently_in_scholarship", "application_needed",
      "first_choice_national_merit", "exclude_from_match", "group_by",
      "first_generation_higher_education", "type", "description"
  ]

  def __repr__(self):
    return "<Scholarship {}>".format(self.name)

  # relationships methods
  def add_ethnicity(self, ethnicity):
    if not self.has_ethnicity(ethnicity.name):
      self.ethnicities.append(ethnicity)

  def add_program(self, program):
    if not self.has_program(program.name):
      self.programs.append(program)

  def remove_ethnicity(self, ethnicity):
    if self.has_ethnicity(ethnicity.name):
      self.ethnicities.remove(ethnicity)

  def remove_program(self, program):
    if self.has_program(program.name):
      self.programs.remove(program)

  def has_ethnicity(self, ethnicity_name):
    return self.ethnicities.filter(
        Ethnicity.name == ethnicity_name).count() > 0

  def has_program(self, program_name):
    return self.programs.filter(Program.name == program_name).count() > 0

  def add_needed_scholarship(self, scholarship):
    if not self.needs_scholarship(scholarship):
      self.scholarships_needed.append(scholarship)

  def remove_needed_scholarship(self, scholarship):
    if self.needs_scholarship(scholarship):
      self.scholarships_needed.remove(scholarship)

  def needs_scholarship(self, scholarship):
    return self.scholarships_needed.filter(
        scholarships_needed.c.needed_id == scholarship.id).count() > 0

  def get_scholarships_needed(self):
    return [{
        "public_id":
            scholarship.public_id,
        "name":
            scholarship.name,
        "url":
            url_for(
                "scholarships.get_scholarship",
                scholarship_id=scholarship.public_id)
    } for scholarship in self.scholarships_needed.all()]

  def get_programs(self):
    return [program.to_dict() for program in self.programs.all()]

  def get_ethnicities(self):
    return [ethnicity.to_dict() for ethnicity in self.ethnicities.all()]

  def for_pagination(self):
    return {
        "name": self.name,
        "public_id": self.public_id,
        "audit_dates": self.audit_dates(),
        "_links": {
            "scholarship":
                url_for(
                    "scholarships.get_scholarship",
                    scholarship_id=self.public_id)
        }
    }

  def to_dict(self):
    return {
        "public_id":
            self.public_id,
        "name":
            self.name,
        "audit_dates":
            self.audit_dates(),
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
        "first_generation_higher_education":
            self.first_generation_higher_education,
        "type":
            self.type,
        "description":
            self.description,
        "programs":
            self.get_programs(),
        "ethnicities":
            self.get_ethnicities(),
        "location_requirement":
            self.location_requirement_endpoints(
                "scholarships.scholarship", scholarship_id=self.public_id),
        "scholarships_needed":
            self.get_scholarships_needed()
    }
