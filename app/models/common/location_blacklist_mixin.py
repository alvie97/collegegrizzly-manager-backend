from flask import url_for
from app import db
from ..consolidated_city import ConsolidatedCity
from ..county import County
from ..place import Place
from ..state import State
from sqlalchemy.ext.declarative import declared_attr
from app.common.errors import LocationEntityError

# TODO: review and improve blacklist, and possibly location_mixin


class LocationBlacklistMixin(object):

  @declared_attr
  def states_blacklist(cls):
    class_name = cls.__name__.lower()
    return db.relationship(
        "State",
        secondary=class_name + "_state_blacklist",
        backref=db.backref(class_name + "_blacklist", lazy="dynamic"),
        lazy="dynamic")

  @declared_attr
  def counties_blacklist(cls):
    class_name = cls.__name__.lower()
    return db.relationship(
        "County",
        secondary=class_name + "_county_blacklist",
        backref=db.backref(class_name + "_blacklist", lazy="dynamic"),
        lazy="dynamic")

  @declared_attr
  def places_blacklist(cls):
    class_name = cls.__name__.lower()
    return db.relationship(
        "Place",
        secondary=class_name + "_place_blacklist",
        backref=db.backref(class_name + "_blacklist", lazy="dynamic"),
        lazy="dynamic")

  @declared_attr
  def consolidated_cities_blacklist(cls):
    class_name = cls.__name__.lower()
    return db.relationship(
        "ConsolidatedCity",
        secondary=class_name + "_consolidated_city_blacklist",
        backref=db.backref(class_name + "_blacklist", lazy="dynamic"),
        lazy="dynamic")

  def get_location_entity_query_blacklist(self, location_obj):
    """
    Returns a tuple of the location entity (Model) and the location requirement
    query object corresponding to that entity in the Model that inherits the
    LocationMixin
    """
    if isinstance(location_obj, State):
      location_query = self.states_blacklist
      location_entity = State
    elif isinstance(location_obj, County):
      location_query = self.counties_blacklist
      location_entity = County
    elif isinstance(location_obj, Place):
      location_query = self.places_blacklist
      location_entity = Place
    elif isinstance(location_obj, ConsolidatedCity):
      location_query = self.consolidated_cities_blacklist
      location_entity = ConsolidatedCity
    else:
      raise LocationEntityError(
          "location object is not an instance of a location")

    return location_entity, location_query

  def add_location_to_blacklist(self, location_obj):
    """
    Adds location obj to Model relationship
    """
    try:
      instance = self.get_location_entity_query_blacklist(location_obj)
    except LocationEntityError:
      raise

    location_entity, location_query = instance

    try:
      if not self.has_location_in_blacklist(location_entity,
                                            location_obj.fips_code):
        location_query.append(location_obj)
    except LocationEntityError:
      raise

  def remove_location_from_blacklist(self, location_obj):
    """
    Removes location obj from Model relationship
    """
    try:
      instance = self.get_location_entity_query_blacklist(location_obj)
    except LocationEntityError:
      raise

    location_entity, location_query = instance

    try:
      if self.has_location_in_blacklist(location_entity,
                                        location_obj.fips_code):
        location_query.remove(location_obj)
    except LocationEntityError:
      raise

  def has_location_in_blacklist(self, location_entity, fips_code):
    """
    Checks if model has a location with the corresponding fips
    """
    if location_entity is State:
      location_query = self.states_blacklist
    elif location_entity is County:
      location_query = self.counties_blacklist
    elif location_entity is Place:
      location_query = self.places_blacklist
    elif location_entity is ConsolidatedCity:
      location_query = self.consolidated_cities_blacklist
    else:
      raise LocationEntityError("location entity is not a location model")

    return location_query.filter(
        location_entity.fips_code == fips_code).count() > 0

  def get_locations_blacklist(self, location_entity, base_endpoint, page,
                              per_page, **endpoint_args):
    """Returns paginated list of locations as a dictionary"""

    if location_entity is State:
      location_name = "states_blacklist"
      location_query = self.states_blacklist
      location_url = base_endpoint + "_states_blacklist"
    elif location_entity is County:
      location_name = "counties_blacklist"
      location_query = self.counties_blacklist
      location_url = base_endpoint + "_counties_blacklist"
    elif location_entity is Place:
      location_name = "places_blacklist"
      location_query = self.places_blacklist
      location_url = base_endpoint + "_places_blacklist"
    elif location_entity is ConsolidatedCity:
      location_name = "consolidated_cities_blacklist"
      location_query = self.consolidated_cities_blacklist
      location_url = base_endpoint + "_consolidated_cities_blacklist"
    else:
      raise LocationEntityError("location entity is not a location model")

    return {
        location_name:
            self.to_collection_dict(location_query, page, per_page,
                                    location_url, **endpoint_args)
    }

  def search_location_in_blacklist(self, search, location_entity,
                                   base_endpoint, page, per_page,
                                   **endpoint_args):
    """Returns paginated list of locations as a dictionary"""

    if location_entity is State:
      location_name = "states_blacklist"
      location_query = self.states_blacklist
      location_url = base_endpoint + "_states_blacklist"
    elif location_entity is County:
      location_name = "counties_blacklist"
      location_query = self.counties_blacklist
      location_url = base_endpoint + "_counties_blacklist"
    elif location_entity is Place:
      location_name = "places_blacklist"
      location_query = self.places_blacklist
      location_url = base_endpoint + "_places_blacklist"
    elif location_entity is ConsolidatedCity:
      location_name = "consolidated_cities_blacklist"
      location_query = self.consolidated_cities_blacklist
      location_url = base_endpoint + "_consolidated_cities_blacklist"
    else:
      raise LocationEntityError("location entity is not a location model")

    query = location_query.filter(
        location_entity.name.like("%{}%".format(search)))

    return {
        location_name:
            self.to_collection_dict(
                query,
                page,
                per_page,
                location_url,
                search=search,
                **endpoint_args)
    }

  def locations_blacklist_endpoints(self, base_endpoint, **endpoint_args):
    """Returns all enpoints to get all location requirements"""
    return {
        "states_blacklist":
            url_for(base_endpoint + "_states_blacklist", **endpoint_args),
        "counties_blacklist":
            url_for(base_endpoint + "_counties_blacklist", **endpoint_args),
        "places_blacklist":
            url_for(base_endpoint + "_places_blacklist", **endpoint_args),
        "consolidated_cities_blacklist":
            url_for(base_endpoint + "_consolidated_cities_blacklist",
                    **endpoint_args)
    }