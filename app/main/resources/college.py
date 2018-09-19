from flask import current_app, request, url_for
from flask_restful import Resource
from marshmallow import ValidationError

from app import db
from app.auth.csrf import csrf_token_required
from app.common.utils import get_entity
from app.models.college import College as CollegeModel
from app.models.major import Major as MajorModel
from app.schemas.college_schema import CollegeSchema
from app.schemas.major_schema import MajorSchema
from app.token_schema import access_token_required

college_schema = CollegeSchema()
major_schema = MajorSchema()
majors_schema = MajorSchema(many=True)


class College(Resource):

  method_decorators = [csrf_token_required, access_token_required]

  @get_entity(CollegeModel, "college")
  def get(self, college: CollegeModel):
    return {"college": college.to_dict()}

  @get_entity(CollegeModel, "college")
  def put(self, college: CollegeModel):
    data = request.get_json() or {}

    if not data:
      return {"message": "no data provided"}, 400

    try:
      college_schema.load(data, partial=True)
    except ValidationError as err:
      return err.messages, 422

    college.update(data)
    db.session.commit()
    return {"college": college.to_dict()}

  @get_entity(CollegeModel, "college")
  def delete(self, college: CollegeModel):
    college.delete()
    db.session.commit()

    return {"message": "college deleted"}


class Colleges(Resource):

  method_decorators = [csrf_token_required, access_token_required]

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
      return {"message": "no data provided"}, 400

    try:
      college = college_schema.load(data)
    except ValidationError as err:
      return err.messages, 422

    db.session.add(college)
    db.session.commit()

    return {"college_id": college.public_id}


class CollegeScholarships(Resource):

  method_decorators = [csrf_token_required, access_token_required]

  @get_entity(CollegeModel, "college")
  def get(self, college: CollegeModel):

    return {
        "scholarships": [{
            "name": scholarship.name,
            "url": url_for(
                "scholarship", scholarship_id=scholarship.public_id)
        } for scholarship in college.scholarships]
    }


class CollegeMajors(Resource):

  method_decorators = [csrf_token_required, access_token_required]

  @get_entity(CollegeModel, "college")
  def get(self, college: CollegeModel):
    return {"majors": college.get_majors()}

  @get_entity(CollegeModel, "college")
  def post(self, college: CollegeModel):
    data = request.get_json() or {}

    if not data or "majors" not in data:
      return {"message": "no data provided"}, 400

    for major in data["majors"]:

      try:
        major_schema.load(major)
      except ValidationError as err:
        return err.messages, 422

      major_to_add = MajorModel.first(name=major["name"])

      if major_to_add is None:
        major_to_add = MajorModel(**major)
        db.session.add(major_to_add)

      college.add_major(major_to_add)

    db.session.commit()
    return {"message": "majors added"}

  @get_entity(CollegeModel, "college")
  def delete(self, college: CollegeModel):
    data = request.get_json() or {}

    if not data or "majors" not in data:
      return {"message": "no data provided"}, 400

    for major in data["majors"]:
      major_to_remove = college.majors.filter_by(name=major).first()

      if major_to_remove is None:
        return {"message": college.name + "doesn't have major " + major}, 404

      college.remove_major(major_to_remove)

    db.session.commit()
    return {"message": "majors removed"}
