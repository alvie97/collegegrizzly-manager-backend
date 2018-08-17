from flask_restful import Resource
from flask import request, current_app
from app import db
from app.models.college import College as CollegeModel
from app.models.major import Major as MajorModel
from app.common.utils import generate_public_id, get_entity


# TODO: use get_entity decorator to get College
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

  @get_entity(CollegeModel, "college")
  def get(self, college_id, entity_obj):
    college = entity_obj
    return {"majors": college.get_majors()}

  @get_entity(CollegeModel, "college")
  def post(self, college_id, entity_obj):
    college = entity_obj
    data = request.get_json() or {}

    if not data or "majors" not in data:
      return {"message": "No data recieved"}, 400

    meta = {"to_add": len(data["majors"]), "added": 0, "failed_to_add": 0}

    added_to_session = False
    for major in data["majors"]:
      major_to_add = MajorModel.query.filter_by(name=major).first()

      if major_to_add is None:
        major_to_add = MajorModel(name=major)
        db.session.add(major_to_add)
        added_to_session = True

      if college.add_major(major_to_add):
        meta["added"] += 1
      else:
        meta["failed_to_add"] += 1

    if added_to_session or meta["added"] > 0:
      db.session.commit()

    return {"_meta": meta}

  @get_entity(CollegeModel, "college")
  def delete(self, college_id, entity_obj):
    college = entity_obj
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
