from flask_restful import Resource
from flask import request, current_app, url_for
from marshmallow import ValidationError

from app import db
from app.models.college import College as CollegeModel
from app.models.major import Major as MajorModel
from app.common.utils import get_entity
from app.schemas.college_schema import CollegeSchema
from app.schemas.major_schema import MajorSchema

college_schema = CollegeSchema()
major_schema = MajorSchema(many=True)


class College(Resource):

  @get_entity(CollegeModel, "college")
  def get(self, college):
    return {"college": college.to_dict()}

  @get_entity(CollegeModel, "college")
  def put(self, college):
    data = request.get_json() or {}

    if not data:
      return {"message": "No data provided"}, 400

    college.update(data)
    db.session.commit()
    return {"college": college.to_dict()}

  @get_entity(CollegeModel, "college")
  def delete(self, college):
    college.delete()
    db.session.commit()

    return {"message": "College deleted"}


class Colleges(Resource):

  def get(self):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get(
        "per_page", current_app.config["COLLEGES_PER_PAGE"], type=int)

    search = request.args.get("search", "", type=str)

    if search:
      query = CollegeModel.query.filter(
          CollegeModel.name.like("%{}%".format(search)))

      data = CollegeModel.to_collection_dict(
          query, page, per_page, "colleges", search=search)
    else:
      query = CollegeModel.query
      data = CollegeModel.to_collection_dict(query, page, per_page, "colleges")

    return data

  def post(self):
    data = request.get_json() or {}

    if not data:
      return {"message": "No data provided"}, 400

    try:
      college = college_schema.load(data)
    except ValidationError as err:
      return err.messages, 422

    db.session.add(college)
    db.session.commit()

    return {"college_id": college.public_id}


class CollegeScholarships(Resource):

  @get_entity(CollegeModel, "college")
  def get(self, college):

    return {
        "scholarships": [{
            "name": scholarship.name,
            "url": url_for(
                "scholarship", scholarship_id=scholarship.public_id)
        } for scholarship in college.scholarships]
    }


class CollegeMajors(Resource):

  @get_entity(CollegeModel, "college")
  def get(self, college):
    return {"majors": college.get_majors()}

  @get_entity(CollegeModel, "college")
  def post(self, college: CollegeModel):
    data = request.get_json() or {}

    if not data or "majors" not in data:
      return {"message": "No data provided"}, 400

    try:
      major_schema.load(data["majors"])
    except ValidationError as err:
      return err.messages, 422

    for major in data["majors"]:
      major_to_add = MajorModel.query.filter_by(name=major["name"]).first()

      if major_to_add is None:
        major_to_add = MajorModel(name=major["name"])
        db.session.add(major_to_add)

      college.add_major(major_to_add)

    db.session.commit()
    return {"message": "majors added"}

  @get_entity(CollegeModel, "college")
  def delete(self, college):
    data = request.get_json() or {}

    if not data or "majors" not in data:
      return {"message": "No data recieved"}, 400

    meta = {
        "to_remove": len(data["majors"]),
        "removed": 0,
        "failed_to_remove": 0
    }

    for major in data["majors"]:
      major_to_remove = MajorModel.query.filter_by(name=major).first()

      if major_to_remove is not None and college.remove_major(major_to_remove):
        meta["removed"] += 1
      else:
        meta["failed_to_remove"] += 1

    if meta["removed"] > 0:
      db.session.commit()

    return {"_meta": meta}
