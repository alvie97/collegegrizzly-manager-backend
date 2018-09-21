from functools import wraps
from uuid import uuid4

from flask import jsonify, request

from app import db
from .errors import LocationEntityError


def generate_public_id():
  return str(uuid4()).replace('-', '')


def get_entity(entity, entity_name):

  def get_entity_decorator(f):

    @wraps(f)
    def f_wrapper(*args, **kwargs):
      entity_obj = entity.first(public_id=kwargs[entity_name + "_id"])

      if entity_obj is None:
        return jsonify({"message": entity_name + " not found"}), 404

      kwargs[entity_name] = entity_obj
      del kwargs[entity_name + "_id"]

      return f(*args, **kwargs)

    return f_wrapper

  return get_entity_decorator


def get_location_requirement(location, entity):
  page = request.args.get("page", 1, type=int)
  per_page = request.args.get("per_page", 15, type=int)

  try:
    locations = entity.get_location_requirement(location, page, per_page)

  except LocationEntityError as err:
    print("LocationEntityError:", err)
    return jsonify({"message": "Error ocurred"}), 500

  return jsonify(locations)


def post_location_requirement(location, entity):
  data = request.get_json() or {}

  if not data or "location_fips" not in data:
    return jsonify({"message": "No data provided"}), 400

  for location_fips in data["location_fips"]:
    location_to_add = location.query.filter_by(fips_code=location_fips).first()

    if location_to_add is not None:
      try:
        entity.add_location(location_to_add)
      except LocationEntityError as err:
        print("LocationEntityError:", err)
        return jsonify({"message": "Error ocurred"}), 500

  db.session.commit()
  return jsonify({"message": "Locations added"})


def delete_location_requirement(location, entity):
  data = request.get_json() or {}

  if not data or "location_fips" not in data:
    return jsonify({"message": "No data provided"}), 400

  for location_fips in data["location_fips"]:
    location_to_delete = location.query.filter_by(
        fips_code=location_fips).first()

    if location is not None:
      try:
        entity.remove_location(location_to_delete)
      except LocationEntityError as err:
        print("LocationEntityError:", err)
        return jsonify({"message": "Error ocurred"}), 500

  db.session.commit()
  return jsonify({"message": "Locations removed"})
