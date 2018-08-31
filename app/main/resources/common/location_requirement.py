from app import db
from app.common.errors import LocationEntityError
from app.common.utils import get_entity_of_resource
from app.models.common import LocationMixin

from flask import request
from flask_restful import Resource

class LocationRequirement(Resource):

  def __init__(self, **kwargs):
    self.entity = kwargs["entity"]
    self.entity_name = kwargs["entity_name"]
    self.location_entity = kwargs["location_entity"]

  @get_entity_of_resource
  def get(self, entity_obj: LocationMixin, **kwargs):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 15, type=int)

    try:
      locations = entity_obj.get_location_requirement(self.location_entity,
                                                      page, per_page)
    except LocationEntityError as err:
      print("LocationEntityError:", err)
      return {"message": "Error ocurred"}, 500

    return locations

  @get_entity_of_resource
  def post(self, entity_obj: LocationMixin, **kwargs):
    data = request.get_json() or {}

    if not data or "location_fips" not in data:
      return {"message": "No data provided"}, 400

    for location_fips in data["location_fips"]:
      location = self.location_entity.query.filter_by(
          fips_code=location_fips).first()

      if location is not None:
        try:
          entity_obj.add_location(location)
        except LocationEntityError as err:
          print("LocationEntityError:", err)

    db.session.commit()
    return {"message": "Locations added"}

  @get_entity_of_resource
  def delete(self, entity_obj: LocationMixin, **kwargs):
    data = request.get_json() or {}

    if not data or "location_fips" not in data:
      return {"message": "No data provided"}, 400

    for location_fips in data["location_fips"]:
      location = self.location_entity.query.filter_by(
          fips_code=location_fips).first()

      if location is not None:
        try:
          entity_obj.remove_location(location)
        except LocationEntityError as err:
          print("LocationEntityError:", err)

    db.session.commit()
    return {"message": "Locations removed"}
