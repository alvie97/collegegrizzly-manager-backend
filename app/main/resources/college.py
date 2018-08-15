from flask_restful import Resource
from flask import request, current_app
from app import db
from app.models.college import College as CollegeModel
from app.models.major import Major as MajorModel
from app.common.utils import generate_public_id, get_college


class College(Resource):

  def get(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()

    if college is None:
      return {"message": "no college found"}, 404

    return college.to_dict()

  def put(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()

    if college is None:
      return {"message": "no college found"}, 404

    data = request.get_json() or {}

    college.from_dict({data["key"]: data["value"]})
    db.session.commit()
    return college.to_dict()


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

  def delete(self):
    data = request.get_json() or {}
    if "public_id" not in data:
      return {"message": "no public_id attribute found"}, 404

    college = CollegeModel.query.filter_by(public_id=data["public_id"])
    college.delete()
    db.session.commit()

    return {"message": "Colleges deleted"}

  def post(self):
    data = request.get_json() or {}

    college = CollegeModel(public_id=generate_public_id(), **data)

    db.session.add(college)
    db.session.commit()

    return college.to_dict()


class CollegeMajors(Resource):

  @get_college
  def get(self, college_id, college):
    return {"majors": college.majors}

  @get_college
  def put(self, college_id, college):
    majors = request.get_json() or {}

    if majors:
      return

    for major in majors:
      if not college.has_major(major):
        new_major = MajorModel.query.filter_by(name=major).first()
        if new_major is None:
          new_major = MajorModel(name=major)
          db.session.add(new_major)
          db.session.commit()
        college.add_major(new_major)

    db.session.commit()
    return {"majors": college.majors}

  @get_college
  def delete(self, college_id, college):
    majors = request.get_json() or {}

    if majors:
      return

    for major in majors:
      if college.has_major(major):
        major_to_delete = MajorModel.query.filter_by(name=major).first()
        college.remove_major(major_to_delete)

    db.session.commit()
    return {"majors": college.majors}
