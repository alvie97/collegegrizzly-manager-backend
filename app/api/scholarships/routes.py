import flask
import marshmallow

import app
from app import scholarships as scholarships_module
from app import security, utils
from app.models import college as college_model
from app.models import consolidated_city as consolidated_city_model
from app.models import county as county_model
from app.models import place as place_model
from app.models import program as program_model
from app.models import scholarship as scholarship_model
from app.models import state as state_model
from app.schemas import program_schema, scholarship_schema

scholarship_schema = scholarship_schema.ScholarshipSchema()
program_schema = program_schema.ProgramSchema()


@scholarships_module.bp.route("/", methods=["GET"], strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_scholarships():
    """Gets scholarships in database

    Retrieves paginated list of all scholarships from database or scholarships that 
    contains the search request parameter if defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant SCHOLARSHIPS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of scholarships.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of scholarships],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
    """
    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page",
        flask.current_app.config["SCHOLARSHIPS_PER_PAGE"],
        type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = scholarship_model.Scholarship.query.filter(
            scholarship_model.Scholarship.name.like("%{}%".format(search)))

        data = scholarship_model.Scholarship.to_collection_dict(
            query,
            page,
            per_page,
            "scholarships.get_scholarships",
            search=search)
    else:
        query = scholarship_model.Scholarship.query
        data = scholarship_model.Scholarship.to_collection_dict(
            query, page, per_page, "scholarships.get_scholarships")

    return flask.jsonify(data)


@scholarships_module.bp.route("/<string:public_id>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship(scholarship):
    """Gets scholarship.

    Retrieves single scholarship from database.

    GET:
        Params:
            public_id (string) (required): public id of scholarship.
    
    Responses:
        200:
            Successfully retieves scholarship. Returns scholarship.

            produces:
                Application/json.
        
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return flask.jsonify({"scholarship": scholarship.to_dict()})


@scholarships_module.bp.route("/<string:public_id>", methods=["PATCH"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def patch_scholarship(scholarship):
    """Edits scholarship.

    PATCH:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            Dictionary of editable scholarship fields.
        
        Example::
            {
                "name": "example scholarship name"
            }
    
    Responses:
        200:
            Scholarship successfully modified. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    data = flask.request.get_json()

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        scholarship_schema.load(data, partial=True)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    scholarship.update(data)
    app.db.session.commit()
    return flask.jsonify("scholarship_model.Scholarship saved successfully")


@scholarships_module.bp.route("/<string:public_id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship(scholarship):
    """Deletes scholarship.

    Deletes scholarship from database.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
    
    Responses:
        200:
            Scholarship successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    app.db.session.delete(scholarship)
    app.db.session.commit()
    return flask.jsonify({"message": "scholarship deleted"})


@scholarships_module.bp.route("/<string:public_id>/programs")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_programs(scholarship):
    """Gets scholarship's programs in database

    Retrieves paginated list of all scholarship's programs from database.

    GET:

    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of programs.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of programs],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return flask.jsonify({"programs": scholarship.get_programs()})


@scholarships_module.bp.route("/<string:public_id>/programs", methods=["POST"])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_programs(scholarship):
    """Creates and adds program to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            Dictionary of editable program fields.
        
        Example::
            {
                "name": "example program name"
            }
    
    Responses:
        201:
            Program successfully created and added to scholarship. 
            Returns scholarship public id.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    program = flask.request.get_json() or {}

    if not program:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        program_schema.load(program)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    program_to_add = program_model.Program.first(
        name=program["name"],
        round_qualification=program["round_qualification"])

    if program_to_add is None:
        program_to_add = program_model.Program(**program)
        app.db.session.add(program_to_add)

    scholarship.add_program(program_to_add)

    app.db.session.commit()
    return flask.jsonify({"message": "programs added"})


@scholarships_module.bp.route(
    "/<string:public_id>/programs", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_programs(scholarship):
    """Removes programs from scholarship.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
        
        Consumes:
            Application/json.
        
        Request body:
            List of programs to remove.

            Example::
                [
                    "program name 1",
                    "program name 2"
                ]

    
    Responses:
        200:
            Programs successfully delete from database. Returns message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    for program in data:

        program_to_remove = scholarship.programs.filter_by(
            name=program["name"],
            round_qualification=program["round_qualification"]).first()

        if program_to_remove is not None:
            scholarship.remove_program(program_to_remove)

    app.db.session.commit()
    return flask.jsonify({"message": "programs removed"})


@scholarships_module.bp.route("/programs_suggestions/name/<string:query>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def programs_suggestions_name(query):
    """Returns programs suggestions

    Retrieves programs suggestions where the program's name contains the query 
    keyword.

    GET:
        Params:
            query (string) (required): Query keyword.
    
    Responses:
        200:
            Returns programs list.

            Produces:
                Application/json.
    """
    suggestions = program_model.Program.query.filter(
        program_model.Program.name.like(f"%{query}%")).limit(5).all()

    return flask.jsonify({
        "suggestions": [suggestion.to_dict() for suggestion in suggestions]
    })


@scholarships_module.bp.route(
    "/programs_suggestions/round_qualification/<string:query>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def programs_suggestions_round(query):
    """Returns programs suggestions

    Retrieves programs suggestions where the program's name contains the query 
    keyword.

    GET:
        Params:
            query (string) (required): Query keyword.
    
    Responses:
        200:
            Returns programs list.

            Produces:
                Application/json.
    """
    suggestions = program_model.Program.query.filter(
        program_model.Program.round_qualification.like(f"%{query}%")).limit(
            5).all()

    return flask.jsonify({
        "suggestions": [suggestion.to_dict() for suggestion in suggestions]
    })


@scholarships_module.bp.route("/<string:public_id>/scholarships_needed")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarships_needed(scholarship):
    """Gets scholarship's scholarships needed in database

    Retrieves paginated list of all scholarship's scholarships needed from database.

    GET:

    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of scholarships needed.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of scholarships needed],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """

    return flask.jsonify({
        "scholarships_needed":
        scholarship.get_scholarships_needed()
    })


@scholarships_module.bp.route(
    "/<string:public_id>/scholarships_needed", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarships_needed(scholarship):
    """adds scholarship needed to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            list of scholarships public ids.
        
        Example::
            ["public id 1", "public id 1"]
    
    Responses:
        200:
            Scholarship needed successfully added to scholarship. Returns 
            message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    college = scholarship.college

    for scholarship_needed in data:
        if scholarship_needed == scholarship.public_id:
            continue

        scholarship_to_add = college.scholarships.filter_by(
            public_id=scholarship_needed).first()

        if scholarship_to_add is not None:
            scholarship.add_needed_scholarship(scholarship_to_add)

    app.db.session.commit()
    return flask.jsonify({"message": "needed scholarships added"})


@scholarships_module.bp.route(
    "/<string:public_id>/scholarships_needed", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarships_needed(scholarship):
    """removes scholarship needed to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            list of scholarships public ids.
        
        Example::
            ["public id 1", "public id 2"]
    
    Responses:
        200:
            Scholarship needed successfully removed from scholarship. Returns
            message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    for scholarship_needed in data:
        scholarship_to_remove = scholarship.scholarships_needed.filter_by(
            public_id=scholarship_needed).first()

        if scholarship_to_remove is not None:
            scholarship.remove_needed_scholarship(scholarship_to_remove)

    app.db.session.commit()
    return flask.jsonify({"message": "needed scholarships removed"})


@scholarships_module.bp.route("/<string:public_id>/states", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_states(scholarship):
    """Gets scholarship's states in database

    Retrieves paginated list of all scholarship's states from database or 
    scholarship's states that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of states.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of states],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """

    return utils.get_location_requirement(
        state_model.State,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route("/<string:public_id>/states", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_states(scholarship):
    """adds states to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            States successfully added to scholarship. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_location_requirement(state_model.State, scholarship)


@scholarships_module.bp.route("/<string:public_id>/states", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_states(scholarship):
    """Removes states from scholarship.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
        
        Consumes:
            Application/json.
        
        Request body:
            List of state FIPS.

            Example::
            ["FIPS 1", "FIPS 2"]

    
    Responses:
        200:
            States successfully deleted from database. Returns message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_location_requirement(state_model.State, scholarship)


@scholarships_module.bp.route("/<string:public_id>/counties", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_counties(scholarship):
    """Gets scholarship's counties in database

    Retrieves paginated list of all scholarship's counties from database or 
    scholarship's counties that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant COUNTIESS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of counties.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of counties],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_location_requirement(
        county_model.County,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route("/<string:public_id>/counties", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_counties(scholarship):
    """adds counties to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Counties successfully added to scholarship. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_location_requirement(county_model.County, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/counties", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_counties(scholarship):
    """Removes counties from scholarship.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
        
        Consumes:
            Application/json.
        
        Request body:
            List of state FIPS.

            Example::
                ["FIPS 1", "FIPS 2"]

    
    Responses:
        200:
            Counties successfully delete from database. Returns message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_location_requirement(county_model.County, scholarship)


@scholarships_module.bp.route("/<string:public_id>/places", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_places(scholarship):
    """Gets scholarship's places in database

    Retrieves paginated list of all scholarship's places from database or 
    scholarship's places that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of places.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of places],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """

    return utils.get_location_requirement(
        place_model.Place,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route("/<string:public_id>/places", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_places(scholarship):
    """adds places to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Places successfully added to scholarship. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_location_requirement(place_model.Place, scholarship)


@scholarships_module.bp.route("/<string:public_id>/places", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_places(scholarship):
    """Removes places from scholarship.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
        
        Consumes:
            Application/json.
        
        Request body:
            List of state FIPS.

            Example::
                ["FIPS 1", "FIPS 2"]

    
    Responses:
        200:
            Places successfully deleted from database. Returns message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_location_requirement(place_model.Place, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_consolidated_cities(scholarship):
    """Gets scholarship's consolidated cities in database

    Retrieves paginated list of all scholarship's consolidated cities from database 
    or scholarship's consolidated cities that contains the search request parameter 
    if defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of consolidated cities.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of consolidated cities],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_location_requirement(
        consolidated_city_model.ConsolidatedCity,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_consolidated_cities(scholarship):
    """adds consolidated cities to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Consolidated cities successfully added to scholarship. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_location_requirement(
        consolidated_city_model.ConsolidatedCity, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_consolidated_cities(scholarship):
    """Removes consolidated cities from scholarship.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
        
        Consumes:
            Application/json.
        
        Request body:
            List of state FIPS.

            Example::
                ["FIPS 1", "FIPS 2"]
    
    Responses:
        200:
            Consolidated cities successfully deleted from database. 
            Returns message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_location_requirement(
        consolidated_city_model.ConsolidatedCity, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_states_blacklist(scholarship):
    """Gets scholarship's states blacklist in database

    Retrieves paginated list of all scholarship's states blacklist from database or 
    scholarship's states blacklist that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of states blacklist.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of states blacklist],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_locations_blacklist(
        state_model.State,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_states_blacklist(scholarship):
    """adds states blacklist to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            States blacklist successfully added to scholarship. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_locations_blacklist(state_model.State, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_states_blacklist(scholarship):
    """Removes states blacklist from scholarship.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
        
        Consumes:
            Application/json.
        
        Request body:
            List of state FIPS.

            Example::
                ["FIPS 1", "FIPS 2"]
    
    Responses:
        200:
            States blacklist successfully deleted from database. Returns message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_locations_blacklist(state_model.State, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_counties_blacklist(scholarship):
    """Gets scholarship's counties blacklist in database

    Retrieves paginated list of all scholarship's counties blacklist from database or 
    scholarship's counties blacklist that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of counties blacklist.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of counties blacklist],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_locations_blacklist(
        county_model.County,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_counties_blacklist(scholarship):
    """adds counties blacklist to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Counties blacklist successfully added to scholarship. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_locations_blacklist(county_model.County, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_counties_blacklist(scholarship):
    """Removes counties blacklist from scholarship.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
        
        Consumes:
            Application/json.
        
        Request body:
            List of state FIPS.

            Example::
                ["FIPS 1", "FIPS 2"]
    
    Responses:
        200:
            Counties blacklist successfully deleted from database. 
            Returns message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_locations_blacklist(county_model.County, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_places_blacklist(scholarship):
    """Gets scholarship's places blacklist in database

    Retrieves paginated list of all scholarship's places blacklist from database or 
    scholarship's places blacklist that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of places blacklist.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of places blacklist],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """

    return utils.get_locations_blacklist(
        place_model.Place,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_places_blacklist(scholarship):
    """adds places blacklist to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Places blacklist successfully added to scholarship. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_locations_blacklist(place_model.Place, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_places_blacklist(scholarship):
    """Removes places blacklist from scholarship.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
        
        Consumes:
            Application/json.
        
        Request body:
            List of state FIPS.

            Example::
                ["FIPS 1", "FIPS 2"]
    
    Responses:
        200:
            Places blacklist successfully deleted from database. Returns message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_locations_blacklist(place_model.Place, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def get_scholarship_consolidated_cities_blacklist(scholarship):
    """Gets scholarship's consolidated cities blacklist in database

    Retrieves paginated list of all scholarship's consolidated cities blacklist 
    from database or scholarship's consolidated cities blacklist that contains the 
    search request parameter if defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of consolidated cities blacklist.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of consolidated cities blacklist],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """

    return utils.get_locations_blacklist(
        consolidated_city_model.ConsolidatedCity,
        "scholarships",
        "scholarship",
        scholarship,
        public_id=scholarship.public_id)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def post_scholarship_consolidated_cities_blacklist(scholarship):
    """adds consolidated cities blacklist to scholarship.

    POST:
        Params:
            public_id (string) (required): public id of scholarship.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Consolidated cities blacklist successfully added to scholarship. 
            Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_locations_blacklist(
        consolidated_city_model.ConsolidatedCity, scholarship)


@scholarships_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(scholarship_model.Scholarship, "public_id")
def delete_scholarship_consolidated_cities_blacklist(scholarship):
    """Removes consolidated cities blacklist from scholarship.

    DELETE:
        Params:
            public_id (string) (required): public id of scholarship.
        
        Consumes:
            Application/json.
        
        Request body:
            List of state FIPS.

            Example::
                ["FIPS 1", "FIPS 2"]
    
    Responses:
        200:
            Consolidated cities blacklist successfully deleted from database. 
            Returns message.

            Produces:
                Application/json.
        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_locations_blacklist(
        consolidated_city_model.ConsolidatedCity, scholarship)
