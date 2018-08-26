from flask import Blueprint
from app import api
bp = Blueprint("main", __name__)

from app.models.college import College as CollegeModel
from app.models.scholarship import Scholarship as ScholarshipModel
from app.models.state import State as StateModel
from app.models.county import County as CountyModel
from app.models.place import Place as PlaceModel
from app.models.consolidated_city import ConsolidatedCity as ConsCityModel

from .resources.college import (College, Colleges, CollegeMajors,
                                CollegeScholarships)
from .resources.scholarship import (Scholarship, Scholarships,
                                    ScholarshipPrograms,
                                    ScholarshipEthnicities, ScholarshipsNeeded)
from .resources.picture import Picture, Pictures
from .resources.file import File
from .resources.locations.usa.states import (States, State, Counties, Places,
                                             ConsolidatedCities)
from .resources.common.utils import LocationRequirement

# Colleges routes

api.add_resource(Colleges, "/colleges", endpoint="colleges")
api.add_resource(College, "/colleges/<string:college_id>", endpoint="college")
# TODO: add majors routes
api.add_resource(CollegeMajors, "/colleges/<string:college_id>/majors")
api.add_resource(
    LocationRequirement,
    "/colleges/<string:college_id>/in_state_requirement/states",
    endpoint="college_in_state_requirement_states",
    resource_class_kwargs={
        "entity": CollegeModel,
        "entity_name": "college",
        "location_entity": StateModel
    })
api.add_resource(
    LocationRequirement,
    "/colleges/<string:college_id>/in_state_requirement/counties",
    endpoint="college_in_state_requirement_counties",
    resource_class_kwargs={
        "entity": CollegeModel,
        "entity_name": "college",
        "location_entity": CountyModel
    })
api.add_resource(
    LocationRequirement,
    "/colleges/<string:college_id>/in_state_requirement/places",
    endpoint="college_in_state_requirement_places",
    resource_class_kwargs={
        "entity": CollegeModel,
        "entity_name": "college",
        "location_entity": PlaceModel
    })

api.add_resource(
    LocationRequirement,
    "/colleges/<string:college_id>"
    "/in_state_requirement/consolidated_cities",
    endpoint="college_in_state_requirement_consolidated_cities",
    resource_class_kwargs={
        "entity": CollegeModel,
        "entity_name": "college",
        "location_entity": ConsCityModel
    })
api.add_resource(
    CollegeScholarships,
    "/colleges/<string:college_id>/scholarships",
    endpoint="college_scholarships")

# Scholarships routes

api.add_resource(
    Scholarships,
    "/colleges/<string:college_id>/scholarships",
    "/scholarships",
    endpoint="scholarships")
api.add_resource(
    Scholarship,
    "/scholarships/<string:scholarship_id>",
    endpoint="scholarship")
api.add_resource(ScholarshipPrograms,
                 "/scholarships/<string:scholarship_id>/programs")
api.add_resource(ScholarshipEthnicities,
                 "/scholarships/<string:scholarship_id>/ethnicities")
api.add_resource(
    ScholarshipsNeeded, "/colleges/<string:college_id>"
    "/scholarships/<string:scholarship_id>/scholarships_needed",
    "/scholarships/<string:scholarship_id>/scholarships_needed")
api.add_resource(
    LocationRequirement,
    "/scholarships/<string:scholarship_id>/location_requirement/states",
    endpoint="scholarship_location_requirement_states",
    resource_class_kwargs={
        "entity": ScholarshipModel,
        "entity_name": "scholarship",
        "location_entity": StateModel
    })

api.add_resource(
    LocationRequirement,
    "/scholarships/<string:scholarship_id>/location_requirement/counties",
    endpoint="scholarship_location_requirement_counties",
    resource_class_kwargs={
        "entity": ScholarshipModel,
        "entity_name": "scholarship",
        "location_entity": CountyModel
    })
api.add_resource(
    LocationRequirement,
    "/scholarships/<string:scholarship_id>/location_requirement/places",
    endpoint="scholarship_location_requirement_places",
    resource_class_kwargs={
        "entity": ScholarshipModel,
        "entity_name": "scholarship",
        "location_entity": PlaceModel
    })
api.add_resource(
    LocationRequirement,
    "/scholarships/<string:scholarship_id>"
    "/location_requirement/consolidated_cities",
    endpoint="scholarship_location_requirement_consolidated_cities",
    resource_class_kwargs={
        "entity": ScholarshipModel,
        "entity_name": "scholarship",
        "location_entity": ConsCityModel
    })

# Pictures routes

api.add_resource(Picture, "/pictures/<string:picture_id>", endpoint="picture")
# TODO: split route in two pictures and CollegePictures
api.add_resource(
    Pictures,
    "/pictures",
    "/colleges/<string:college_id>/pictures",
    endpoint="pictures")
api.add_resource(File, "/file/<path:folder>/<path:filename>", endpoint="file")

# Locations routes
# TODO: single locations routes
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
