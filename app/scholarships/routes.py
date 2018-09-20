from flask import current_app, request
from flask_restful import Resource
from marshmallow import ValidationError

from app import db
from app.common.utils import generate_public_id, get_entity
from app.models.college import College as CollegeModel
from app.models.ethnicity import Ethnicity as EthnicityModel
from app.models.program import Program as ProgramModel
from app.models.scholarship import Scholarship as ScholarshipModel
from app.schemas.ethnicity_schema import EthnicitySchema
from app.schemas.program_schema import ProgramSchema
from app.schemas.scholarship_schema import ScholarshipSchema

from . import bp

scholarship_schema = ScholarshipSchema()
program_schema = ProgramSchema()
ethnicity_schema = EthnicitySchema()


@bp.route("/<string:scholarship_id>")
@get_entity(ScholarshipModel, "scholarship")
def get_scholarship(self, scholarship):

  return {"scholarship": scholarship.to_dict()}


@bp.route("/<string:scholarship_id>", methods=["PATCH"])
@get_entity(ScholarshipModel, "scholarship")
def patch_scholarship(self, scholarship):
  data = request.get_json()

  if not data:
    return {"message": "no data provided"}, 400

  try:
    scholarship_schema.load(data, partial=True)
  except ValidationError as err:
    return err.messages, 422

  scholarship.update(data)
  db.session.commit()
  return {"scholarship": scholarship.to_dict()}


@bp.route("/<string:scholarship_id>", methods=["DELETE"])
@get_entity(ScholarshipModel, "scholarship")
def delete_scholarship(self, scholarship):

  db.session.delete(scholarship)
  db.session.commit()
  return {"message": "scholarship deleted"}


@bp.route("/", methods=["GET"])
def get_scholarships(self):
  page = request.args.get("page", 1, type=int)
  per_page = request.args.get(
      "per_page", current_app.config["SCHOLARSHIPS_PER_PAGE"], type=int)

  return ScholarshipModel.to_collection_dict(ScholarshipModel.query, page,
                                             per_page, "scholarships")


@bp.route("/<string:college_id>", methods=["POST"])
@get_entity(CollegeModel, "college")
def post_scholarship(self, college):
  data = request.get_json()

  if not data:
    return {"message": "no data provided"}, 400

  try:
    scholarship_schema.load(data)
  except ValidationError as err:
    return err.messages, 422

  scholarship = ScholarshipModel(
      public_id=generate_public_id(), college=college, **data)

  db.session.add(scholarship)
  db.session.commit()

  return {"scholarship_id": scholarship.public_id}


@bp.route("/<string:scholarship_id>/programs")
@get_entity(ScholarshipModel, "scholarship")
def get_scholarship_majors(self, scholarship):
  return {"programs": scholarship.get_programs()}


@bp.route("/<string:scholarship_id>/programs", methods=["POST"])
@get_entity(ScholarshipModel, "scholarship")
def post_scholarship_majors(self, scholarship):
  data = request.get_json() or {}

  if not data or "programs" not in data:
    return {"message": "no data provided"}, 400

  for program in data["programs"]:
    try:
      program_schema.load(program)
    except ValidationError as err:
      return err.messages, 422

    program_to_add = ProgramModel.first(name=program["name"])

    if program_to_add is None:
      program_to_add = ProgramModel(**program)
      db.session.add(program_to_add)

    scholarship.add_program(program_to_add)

  db.session.commit()
  return {"message": "programs added"}


@bp.route("/<string:scholarship_id>/programs", methods=["DELETE"])
@get_entity(ScholarshipModel, "scholarship")
def delete_scholarship_majors(self, scholarship):
  data = request.get_json() or {}

  if not data or "programs" not in data:
    return {"message": "no data provided"}, 400

  for program in data["programs"]:
    program_to_remove = scholarship.programs.filter_by(name=program).first()

    if program_to_remove is None:
      return {
          "message": scholarship.name + "doesn't have program " + program
      }, 404

    scholarship.remove_program(program_to_remove)

  db.session.commit()
  return {"message": "programs removed"}


@bp.route("/<string:scholarship_id>/ethnicities")
@get_entity(ScholarshipModel, "scholarship")
def get_scholarship_ethnicities(self, scholarship):
  return {"ethnicities": scholarship.get_ethnicities()}


@bp.route("/<string:scholarship_id>/ethnicities", methods=["POST"])
@get_entity(ScholarshipModel, "scholarship")
def post_scholarship_ethnicities(self, scholarship):
  data = request.get_json() or {}

  if not data or "ethnicities" not in data:
    return {"message": "no data provided"}, 400

  for ethnicity in data["ethnicities"]:
    try:
      ethnicity_schema.load(ethnicity)
    except ValidationError as err:
      return err.messages, 422

    ethnicity_to_add = EthnicityModel.first(name=ethnicity["name"])

    if ethnicity_to_add is None:
      ethnicity_to_add = EthnicityModel(**ethnicity)
      db.session.add(ethnicity_to_add)

    scholarship.add_ethnicity(ethnicity_to_add)

  db.session.commit()
  return {"message": "ethnicities added"}


@bp.route("/<string:scholarship_id>/ethnicities", methods=["DELETE"])
@get_entity(ScholarshipModel, "scholarship")
def delete_scholarship_ethnicities(self, scholarship):
  data = request.get_json() or {}

  if not data or "ethnicities" not in data:
    return {"message": "no data provided"}, 400

  for ethnicity in data["ethnicities"]:
    ethnicity_to_remove = scholarship.ethnicities.filter_by(
        name=ethnicity).first()

    if ethnicity_to_remove is None:
      return {
          "message": scholarship.name + "doesn't have ethnicity " + ethnicity
      }, 404

    scholarship.remove_ethnicity(ethnicity_to_remove)

  db.session.commit()
  return {"message": "ethnicities removed"}


@bp.route("/<string:scholarship_id>/scholarships_needed")
@get_entity(ScholarshipModel, "scholarship")
def get(self, scholarship):

  return {"scholarships_needed": scholarship.get_scholarships_needed()}


@bp.route("/<string:scholarship_id>/scholarships_needed", methods=["POST"])
@get_entity(ScholarshipModel, "scholarship")
def post(self, scholarship):
  data = request.get_json() or {}

  if not data or "scholarships_needed" not in data:
    return {"message": "no data provided"}, 400

  college = scholarship.college

  for scholarship_needed in data["scholarships_needed"]:
    if scholarship_needed == scholarship.public_id:
      continue

    scholarship_to_add = college.scholarships.filter_by(
        public_id=scholarship_needed).first()

    if scholarship_to_add is not None:
      scholarship.add_needed_scholarship(scholarship_to_add)

  db.session.commit()
  return {"message": "needed scholarships added"}


@bp.route("/<string:scholarship_id>/scholarships_needed", methods=["DELETE"])
@get_entity(ScholarshipModel, "scholarship")
def delete(self, scholarship):
  data = request.get_json() or {}

  if not data or "scholarships_needed" not in data:
    return {"message": "no data provided"}, 400

  for scholarship_needed in data["scholarships_needed"]:
    scholarship_to_remove = scholarship.scholarships_needed.filter_by(
        public_id=scholarship_needed).first()

    if scholarship_to_remove is not None:
      scholarship.remove_needed_scholarship(scholarship_to_remove)

  db.session.commit()
  return {"message": "needed scholarships removed"}
