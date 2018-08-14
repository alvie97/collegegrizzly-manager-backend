from flask import Blueprint
from app import api

bp = Blueprint("main", __name__)

from .resources.college import College, Colleges, InStateRequirement, Majors
from .resources.scholarship import Scholarship, Scholarships
from .resources.picture import Picture, Pictures
from .resources.file import File
from .resources.locations.usa.states import (States, State, Counties, Places,
                                             ConsolidatedCities)

api.add_resource(College, "/colleges/<string:college_id>", endpoint="college")
api.add_resource(Colleges, "/colleges", endpoint="colleges")
api.add_resource(InStateRequirement,
                 "/colleges/<string:college_id>/in_state_requirement")
api.add_resource(Majors, "/colleges/<string:college_id>/majors")
api.add_resource(
    Scholarship,
    "/scholarships/<string:scholarship_id>",
    endpoint="scholarship")
api.add_resource(
    Scholarships,
    "/scholarships",
    "/colleges/<string:college_id>/scholarships",
    endpoint="scholarships")
api.add_resource(Picture, "/pictures/<string:picture_id>", endpoint="picture")
api.add_resource(
    Pictures,
    "/pictures",
    "/colleges/<string:college_id>/pictures",
    endpoint="pictures")
api.add_resource(File, "/file/<path:folder>/<path:filename>", endpoint="file")
api.add_resource(States, "/locations/usa/states")
api.add_resource(State, "/locations/usa/states/<string:fips_code>")
api.add_resource(
    Counties,
    "/locations/usa/states/<string:state_fips>/counties",
    "/locations/usa/counties",
    endpoint="usa_state_counties")
api.add_resource(
    Places,
    "/locations/usa/states/<string:state_fips>/places",
    "/locations/usa/places",
    endpoint="usa_state_places")
api.add_resource(
    ConsolidatedCities,
    "/locations/usa/states/<string:state_fips>/consolidated_cities",
    "/locations/usa/consolidated_cities",
    endpoint="usa_state_consolidated_cities")
