from flask import request
from flask_restful import Resource

from app import db
from app.common.utils import get_entity


class LocationRequirement(Resource):

  def __init__(self, **kwargs):
    self.entity = kwargs["entity"]
    self.location_entity = kwargs["location_entity"]

  @get_entity
  def get(self, entity_obj_id, entity_obj):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 15, type=int)

    return entity_obj.get_location_requirement(self.location_entity, page,
                                               per_page)

  @get_entity
  def post(self, entity_obj_id, entity_obj):
    data = request.get_json() or {}

    if data:
      meta = {
          "to_add": len(data["location_fips"]),
          "added": 0,
          "failed_to_add": 0
      }

      for location_fips in data["location_fips"]:
        location = self.location_entity.query.filter_by(
            fips_code=location_fips).first()

        if location is None or not entity_obj.add_location(location):
          meta["failed_to_add"] += 1
        else:
          meta["added"] += 1

      db.session.commit()
      return {"_meta": meta}

    return {"message": "No data provided"}, 404

  @get_entity
  def delete(self, entity_obj_id, entity_obj):
    data = request.get_json() or {}

    if data:

      meta = {
          "to_remove": len(data["location_fips"]),
          "removed": 0,
          "failed_to_remove": 0
      }

      for location_fips in data["location_fips"]:
        location = self.location_entity.query.filter_by(
            fips_code=location_fips).first()

        if location is None or not entity_obj.remove_location(location):
          meta["failed_to_remove"] += 1
        else:
          meta["removed"] += 1

      db.session.commit()
      return {"_meta": meta}

    return {"message": "No data provided"}, 404
