from flask_restful import Resource
from flask import request, current_app
from app import db
from app.models.scholarship import Scholarship as ScholarshipModel
from app.models.college import College as CollegeModel
from app.models.program import Program as ProgramModel
from app.models.ethnicity import Ethnicity as EthnicityModel
from app.common.utils import generate_public_id, get_entity


# TODO: use get entity decorator to get scholarships
class Scholarship(Resource):

  def get(self, scholarship_id):
    scholarship = ScholarshipModel.query.filter_by(
        public_id=scholarship_id).first()

    if scholarship is None:
      return {"message": "no scholarship found"}, 404

    return scholarship.to_dict()

  def put(self, scholarship_id):
    scholarship = ScholarshipModel.query.filter_by(
        public_id=scholarship_id).first()

    if scholarship is None:
      return {"message": "no scholarship found"}, 404

    data = request.get_json()
    scholarship.from_dict({data["key"]: data["value"]})
    db.session.commit()
    return data

  def delete(self, scholarship_id):
    scholarship = ScholarshipModel.query.filter_by(
        public_id=scholarship_id).first()

    if scholarship is None:
      return {"message": "no scholarship found"}, 404

    db.session.delete(scholarship)
    db.session.commit()
    return {"message": "scholarship deleted"}


class Scholarships(Resource):

  def get(self, college_id=None):
    if college_id is not None:
      college = CollegeModel.query.filter_by(public_id=college_id).first()
      if college is None:
        return {"message": "College not found"}, 404

      resources = college.scholarships.all()
      data = {"items": [item.to_dict() for item in resources]}

      return data

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get(
        "per_page", current_app.config["SCHOLARSHIPS_PER_PAGE"], type=int)

    data = ScholarshipModel.to_collection_dict(ScholarshipModel.query, page,
                                               per_page, "scholarships")

    return data

  def post(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()

    if college is None:
      return {"message": "college not found"}, 404

    data = request.get_json()

    scholarship = ScholarshipModel(
        public_id=generate_public_id(), college=college, **data)
    db.session.add(scholarship)
    db.session.commit()

    return scholarship.public_id


class ScholarshipPrograms(Resource):

  @get_entity(ScholarshipModel, "scholarship")
  def get(self, scholarship_id, entity_obj):
    scholarship = entity_obj
    return {"programs": scholarship.get_programs()}

  @get_entity(ScholarshipModel, "scholarship")
  def post(self, scholarship_id, entity_obj):
    scholarship = entity_obj
    data = request.get_json() or {}

    if not data or "programs" not in data:
      return {"message": "No data provided"}, 400

    meta = {"to_add": len(data["programs"]), "added": 0, "failed_to_add": 0}

    created = False
    for program in data["programs"]:
      program_to_add = ProgramModel.query.filter_by(
          name=program["name"]).first()

      if program_to_add is None:
        program_to_add = ProgramModel(
            name=program["name"],
            round_qualification=program["round_qualification"])
        db.session.add(program_to_add)
        created = True

      if scholarship.add_program(program_to_add):
        meta["added"] += 1
      else:
        meta["failed_to_add"] += 1

    if meta["added"] > 0 or created:
      db.session.commit()

    return {"_meta": meta}

  @get_entity(ScholarshipModel, "scholarship")
  def delete(self, scholarship_id, entity_obj):
    scholarship = entity_obj
    data = request.get_json() or {}

    if not data or "programs" not in data:
      return {"message": "No data provided"}, 400

    meta = {
        "to_remove": len(data["programs"]),
        "removed": 0,
        "failed_to_remove": 0
    }

    for program in data["programs"]:
      program_to_remove = ProgramModel.query.filter_by(
          name=program["name"]).first()

      if program_to_remove is not None and scholarship.remove_program(
          program_to_remove):
        meta["removed"] += 1
      else:
        meta["failed_to_remove"] += 1

    if meta["removed"] > 0:
      db.session.commit()

    return {"_meta": meta}

class ScholarshipEthnicities(Resource):

  @get_entity(ScholarshipModel, "scholarship")
  def get(self, scholarship_id, entity_obj):
    scholarship = entity_obj
    return {"ethnicities": scholarship.get_ethnicities()}

  @get_entity(ScholarshipModel, "scholarship")
  def post(self, scholarship_id, entity_obj):
    scholarship = entity_obj
    data = request.get_json() or {}

    if not data or "ethnicities" not in data:
      return {"message": "No data provided"}, 400

    meta = {"to_add": len(data["ethnicities"]), "added": 0, "failed_to_add": 0}

    created = False
    for ethnicity in data["ethnicities"]:
      ethnicity_to_add = EthnicityModel.query.filter_by(
          name=ethnicity["name"]).first()

      if ethnicity_to_add is None:
        ethnicity_to_add = EthnicityModel(
            name=ethnicity["name"])
        db.session.add(ethnicity_to_add)
        created = True

      if scholarship.add_ethnicity(ethnicity_to_add):
        meta["added"] += 1
      else:
        meta["failed_to_add"] += 1

    if meta["added"] > 0 or created:
      db.session.commit()

    return {"_meta": meta}

  @get_entity(ScholarshipModel, "scholarship")
  def delete(self, scholarship_id, entity_obj):
    scholarship = entity_obj
    data = request.get_json() or {}

    if not data or "ethnicities" not in data:
      return {"message": "No data provided"}, 400

    meta = {
        "to_remove": len(data["ethnicities"]),
        "removed": 0,
        "failed_to_remove": 0
    }

    for ethnicity in data["ethnicities"]:
      ethnicity_to_remove = EthnicityModel.query.filter_by(
          name=ethnicity["name"]).first()

      if ethnicity_to_remove is not None and scholarship.remove_ethnicity(
          ethnicity_to_remove):
        meta["removed"] += 1
      else:
        meta["failed_to_remove"] += 1

    if meta["removed"] > 0:
      db.session.commit()

    return {"_meta": meta}
