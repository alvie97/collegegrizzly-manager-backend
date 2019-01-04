from flask import url_for
from app import db
from sqlalchemy.orm.query import Query as SqlalchemyQuery
from typing import Tuple
from ..consolidated_city import ConsolidatedCity
from ..county import County
from ..place import Place
from ..state import State
from sqlalchemy.ext.declarative import declared_attr
from app.common.errors import LocationEntityError


class LocationMixin(object):

    @declared_attr
    def location_requirement_states(cls):
        class_name = cls.__name__.lower()
        return db.relationship(
            "State",
            secondary=class_name + "_state",
            backref=db.backref(class_name + "_list", lazy="dynamic"),
            lazy="dynamic")

    @declared_attr
    def location_requirement_counties(cls):
        class_name = cls.__name__.lower()
        return db.relationship(
            "County",
            secondary=class_name + "_county",
            backref=db.backref(class_name + "_list", lazy="dynamic"),
            lazy="dynamic")

    @declared_attr
    def location_requirement_places(cls):
        class_name = cls.__name__.lower()
        return db.relationship(
            "Place",
            secondary=class_name + "_place",
            backref=db.backref(class_name + "_list", lazy="dynamic"),
            lazy="dynamic")

    @declared_attr
    def location_requirement_consolidated_cities(cls):
        class_name = cls.__name__.lower()
        return db.relationship(
            "ConsolidatedCity",
            secondary=class_name + "_consolidated_city",
            backref=db.backref(class_name + "_list", lazy="dynamic"),
            lazy="dynamic")

    def get_location_entity_query(self, location_obj):
        """
    Returns a tuple of the location entity (Model) and the location requirement
    query object corresponding to that entity in the Model that inherits the
    LocationMixin
    """
        if isinstance(location_obj, State):
            location_query = self.location_requirement_states
            location_entity = State
        elif isinstance(location_obj, County):
            location_query = self.location_requirement_counties
            location_entity = County
        elif isinstance(location_obj, Place):
            location_query = self.location_requirement_places
            location_entity = Place
        elif isinstance(location_obj, ConsolidatedCity):
            location_query = self.location_requirement_consolidated_cities
            location_entity = ConsolidatedCity
        else:
            raise LocationEntityError(
                "location object is not an instance of a location")

        return location_entity, location_query

    def add_location(self, location_obj):
        """
    Adds location obj to Model relationship
    """
        try:
            instance = self.get_location_entity_query(location_obj)
        except LocationEntityError:
            raise

        location_entity, location_query = instance

        try:
            if not self.has_location(location_entity, location_obj.fips_code):
                location_query.append(location_obj)
        except LocationEntityError:
            raise

    def remove_location(self, location_obj):
        """
    Removes location obj from Model relationship
    """
        try:
            instance = self.get_location_entity_query(location_obj)
        except LocationEntityError:
            raise

        location_entity, location_query = instance

        try:
            if self.has_location(location_entity, location_obj.fips_code):
                location_query.remove(location_obj)
        except LocationEntityError:
            raise

    def has_location(self, location_entity, fips_code):
        """
    Checks if model has a location with the corresponding fips
    """
        if location_entity is State:
            location_query = self.location_requirement_states
        elif location_entity is County:
            location_query = self.location_requirement_counties
        elif location_entity is Place:
            location_query = self.location_requirement_places
        elif location_entity is ConsolidatedCity:
            location_query = self.location_requirement_consolidated_cities
        else:
            raise LocationEntityError(
                "location entity is not a location model")

        return location_query.filter(
            location_entity.fips_code == fips_code).count() > 0

    def get_location_requirement(self, location_entity, base_endpoint, page,
                                 per_page, **endpoint_args):
        """Returns paginated list of locations as a dictionary"""

        if location_entity is State:
            location_name = "states"
            location_query = self.location_requirement_states
            location_url = base_endpoint + "_states"
        elif location_entity is County:
            location_name = "counties"
            location_query = self.location_requirement_counties
            location_url = base_endpoint + "_counties"
        elif location_entity is Place:
            location_name = "places"
            location_query = self.location_requirement_places
            location_url = base_endpoint + "_places"
        elif location_entity is ConsolidatedCity:
            location_name = "consolidated_cities"
            location_query = self.location_requirement_consolidated_cities
            location_url = base_endpoint + "_consolidated_cities"
        else:
            raise LocationEntityError(
                "location entity is not a location model")

        return {
            location_name:
            self.to_collection_dict(location_query, page, per_page,
                                    location_url, **endpoint_args)
        }

    def search_location_requirement(self, search, location_entity,
                                    base_endpoint, page, per_page,
                                    **endpoint_args):
        """Returns paginated list of locations as a dictionary"""

        if location_entity is State:
            location_name = "states"
            location_query = self.location_requirement_states
            location_url = base_endpoint + "_states"
        elif location_entity is County:
            location_name = "counties"
            location_query = self.location_requirement_counties
            location_url = base_endpoint + "_counties"
        elif location_entity is Place:
            location_name = "places"
            location_query = self.location_requirement_places
            location_url = base_endpoint + "_places"
        elif location_entity is ConsolidatedCity:
            location_name = "consolidated_cities"
            location_query = self.location_requirement_consolidated_cities
            location_url = base_endpoint + "_consolidated_cities"
        else:
            raise LocationEntityError(
                "location entity is not a location model")

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

    def location_requirement_endpoints(self, base_endpoint, **endpoint_args):
        """Returns all enpoints to get all location requirements"""
        return {
            "states":
            url_for(base_endpoint + "_states", **endpoint_args),
            "counties":
            url_for(base_endpoint + "_counties", **endpoint_args),
            "places":
            url_for(base_endpoint + "_places", **endpoint_args),
            "consolidated_cities":
            url_for(base_endpoint + "_consolidated_cities", **endpoint_args)
        }
