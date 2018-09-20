from functools import wraps
from typing import Any, Callable, Dict, Tuple, Union
from uuid import uuid4

from flask_sqlalchemy.model import Model
from flask import jsonify

from app.models.common.base_mixin import BaseMixin

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


def get_entity_of_resource(entity, entity_name):

  def decorator_wrapper(f):

    @wraps(f)
    def f_wrapper(*args, **kwargs):
      entity_obj = entity.first(public_id=kwargs[entity_name + "_id"])
      if entity_obj is None:
        return jsonify({"message": "entity not found"}), 404

      return f(entity_obj=entity_obj, *args, **kwargs)

    return f_wrapper

  return decorator_wrapper


def get_location_requirement(location, entity, entity_name):
  page = request.args.get("page", 1, type=int)
  per_page = request.args.get("per_page", 15, type=int)

  try:
    locations = entity.get_location_requirement(location, page, per_page)

  except LocationEntityError as err:
    print("LocationEntityError:", err)
    return jsonify({"message": "Error ocurred"}), 500

  return jsonify(locations)


def post_location_requirement(location, entity, entity_name):
  data = request.get_json() or {}

  if not data or "location_fips" not in data:
    return jsonify({"message": "No data provided"}), 400

  for location_fips in data["location_fips"]:
    location = self.location_entity.query.filter_by(
        fips_code=location_fips).first()

    if location is not None:
      try:
        entity_obj.add_location(location)
      except LocationEntityError as err:
        print("LocationEntityError:", err)
      return jsonify({"message": "Error ocurred"}), 500

  db.session.commit()
  return jsonify({"message": "Locations added"})


def delete_location_requirement(location, entity, entity_name):
  data = request.get_json() or {}

  if not data or "location_fips" not in data:
    return jsonify({"message": "No data provided"}), 400

  for location_fips in data["location_fips"]:
    location = self.location_entity.query.filter_by(
        fips_code=location_fips).first()

    if location is not None:
      try:
        entity_obj.remove_location(location)
      except LocationEntityError as err:
        print("LocationEntityError:", err)
      return jsonify({"message": "Error ocurred"}), 500

  db.session.commit()
  return jsonify({"message": "Locations removed"})
