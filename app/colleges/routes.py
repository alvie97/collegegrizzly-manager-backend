import flask
import marshmallow

import app
from app import colleges as colleges_module
from app import security, utils
from app.models import college as college_model
from app.models import consolidated_city as consolidated_city_model
from app.models import county as county_model
from app.models import major as major_model
from app.models import picture as picture_model
from app.models import place as place_model
from app.models import scholarship as scholarship_model
from app.models import state as state_model
from app.schemas import college_schema
from app.schemas import major_schema as major_sc
from app.schemas import scholarship_schema

college_schema = college_schema.CollegeSchema()
major_schema = major_sc.MajorSchema()
majors_schema = major_sc.MajorSchema(many=True)
scholarship_schema = scholarship_schema.ScholarshipSchema()


@colleges_module.bp.route("/", methods=["GET"], strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_colleges():
    """Gets colleges in database

    Retrieves paginated list of all colleges from database or colleges that 
    contains the search request parameter if defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant COLLEGE_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of colleges.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of colleges],
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
        "per_page", flask.current_app.config["COLLEGES_PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = college_model.College.query.filter(
            college_model.College.name.like("%{}%".format(search)))

        data = college_model.College.to_collection_dict(
            query, page, per_page, "colleges.get_colleges", search=search)
    else:
        query = college_model.College.query
        data = college_model.College.to_collection_dict(
            query, page, per_page, "colleges.get_colleges")

    return flask.jsonify(data)


#TODO: Return college url instead of college public id.
@colleges_module.bp.route("/", methods=["POST"], strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def post_college():
    """Creates college.

    Creates, validates and adds college to database.

    Post:
        Consumes:
            Application/json.
        Request body:
            Editable colleges fields. See college model.
        
            Example::
                {
                    "name": "example name"
                }
    Responses:
        201:
            Successfully created college. Returns college public id.

            produces:
                Application/json.

            Example::
                {
                    "college_id": uuid string without dashes
                }
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        422:
            some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        college = college_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    app.db.session.add(college)
    app.db.session.commit()

    return flask.jsonify({"college_id": college.public_id}), 201


@colleges_module.bp.route("/<string:public_id>", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college(college):
    """Gets college.

    Retrieves single college from database.

    GET:
        Params:
            public_id (string) (required): public id of college.
    
    Responses:
        200:
            Successfully retieves college. Returns college.

            produces:
                Application/json.
        
        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    return flask.jsonify(college.to_dict())


@colleges_module.bp.route("/<string:public_id>", methods=["PATCH"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def patch_college(college):
    """Edits college.

    Modifies college model.

    PATCH:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            Dictionary of editable college fields.
        
        Example::
            {
                "name": "example college name"
            }
    
    Responses:
        200:
            College successfully modified. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        college_schema.load(data, partial=True)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    college.update(data)
    app.db.session.commit()
    return flask.jsonify({"message": "college saved successfully"})


@colleges_module.bp.route("/<string:public_id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college(college):
    """Deletes college.

    Deletes college from database.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
    
    Responses:
        200:
            College successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    college.delete()
    app.db.session.commit()

    return flask.jsonify({"message": "college deleted"})


@colleges_module.bp.route("/<string:public_id>/scholarships", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_scholarships(college):
    """Gets college's scholarships in database

    Retrieves paginated list of all college's scholarships from database or 
    college's scholarships that contains the search request parameter if 
    defined.

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
            of colleges.

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
        404:
            College not found, returns message.

            produces:
                Application/json.
    """

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page",
        flask.current_app.config["SCHOLARSHIPS_PER_PAGE"],
        type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = college.scholarships.filter(
            scholarship_model.Scholarship.name.like("%{}%".format(search)))

        data = scholarship_model.Scholarship.to_collection_dict(
            query,
            page,
            per_page,
            "scholarships.get_scholarships",
            search=search)
    else:
        query = college.scholarships
        data = scholarship_model.Scholarship.to_collection_dict(
            query, page, per_page, "scholarships.get_scholarships")
    return flask.jsonify({"scholarships": data})


@colleges_module.bp.route("/<string:public_id>/scholarships", methods=["POST"])
@utils.get_entity(college_model.College, "public_id")
def post_college_scholarship(college):
    """Creates and adds scholarship to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            Dictionary of editable scholarship fields.
        
        Example::
            {
                "name": "example scholarship name"
            }
    
    Responses:
        201:
            Scholarship successfully created and added to college. 
            Returns scholarship public id.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

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
        scholarship_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

    scholarship = scholarship_model.Scholarship(
        public_id=utils.generate_public_id(), college=college, **data)

    app.db.session.add(scholarship)
    app.db.session.commit()

    return flask.jsonify({"scholarship_id": scholarship.public_id}), 201


@colleges_module.bp.route("/<string:public_id>/majors", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_majors(college):
    """Gets college's majors in database

    Retrieves paginated list of all college's majors from database or 
    college's majors that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant MAJORS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of majors.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of majors],
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return flask.jsonify({"majors": college.get_majors()})


@colleges_module.bp.route("/<string:public_id>/majors", methods=["POST"])
@utils.get_entity(college_model.College, "public_id")
def post_college_majors(college):
    """Creates and adds major to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            Dictionary of editable major fields.
        
        Example::
            {
                "name": "example major name"
            }
    
    Responses:
        201:
            Major successfully created and added to college. 
            Returns scholarship public id.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data or "majors" not in data:
        return flask.jsonify({"message": "no data provided"}), 400

    for major in data["majors"]:

        try:
            major_schema.load(major)
        except marshmallow.ValidationError as err:
            return flask.jsonify(err.messages), 422

        major_to_add = major_model.Major.first(name=major["name"])

        if major_to_add is None:
            major_to_add = major_model.Major(**major)
            app.db.session.add(major_to_add)

        college.add_major(major_to_add)

    app.db.session.commit()
    return flask.jsonify({"message": "majors added"}), 201


@colleges_module.bp.route("/<string:public_id>/majors", methods=["DELETE"])
@utils.get_entity(college_model.College, "public_id")
def delete_college_majors(college):
    """Removes majors from college.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
        
        Consumes:
            Application/json.
        
        Request body:
            List of majors to remove.

            Example::
                [
                    {major 1},
                    {major 2}
                ]

                See major model.

    
    Responses:
        200:
            Majors successfully delete from database. Returns message.

            Produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    for major in data:
        major_to_remove = college.majors.filter_by(name=major).first()

        if major_to_remove is None:
            return flask.jsonify({
                "message":
                college.name + "doesn't have major " + major
            }), 404

        college.remove_major(major_to_remove)

    app.db.session.commit()
    return flask.jsonify({"message": "majors removed"})


@colleges_module.bp.route("/<string:public_id>/states", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_states(college):
    """Gets college's states in database

    Retrieves paginated list of all college's states from database or 
    college's states that contains the search request parameter if 
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_location_requirement(
        state_model.State,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route("/<string:public_id>/states", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_states(college):
    """adds states to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            States successfully added to college. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_location_requirement(state_model.State, college)


@colleges_module.bp.route("/<string:public_id>/states", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_states(college):
    """Removes states from college.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
        
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_location_requirement(state_model.State, college)


@colleges_module.bp.route("/<string:public_id>/counties", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_counties(college):
    """Gets college's counties in database

    Retrieves paginated list of all college's counties from database or 
    college's counties that contains the search request parameter if 
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_location_requirement(
        county_model.County,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route("/<string:public_id>/counties", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_counties(college):
    """adds counties to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Counties successfully added to college. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_location_requirement(county_model.County, college)


@colleges_module.bp.route("/<string:public_id>/counties", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_counties(college):
    """Removes counties from college.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
        
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_location_requirement(county_model.County, college)


@colleges_module.bp.route("/<string:public_id>/places", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_places(college):
    """Gets college's places in database

    Retrieves paginated list of all college's places from database or 
    college's places that contains the search request parameter if 
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_location_requirement(
        place_model.Place,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route("/<string:public_id>/places", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_places(college):
    """adds places to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Places successfully added to college. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_location_requirement(place_model.Place, college)


@colleges_module.bp.route("/<string:public_id>/places", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_places(college):
    """Removes places from college.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
        
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_location_requirement(place_model.Place, college)


@colleges_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_consolidated_cities(college):
    """Gets college's consolidated cities in database

    Retrieves paginated list of all college's consolidated cities from database 
    or college's consolidated cities that contains the search request parameter 
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_location_requirement(
        consolidated_city_model.ConsolidatedCity,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_consolidated_cities(college):
    """adds consolidated cities to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Consolidated cities successfully added to college. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_location_requirement(
        consolidated_city_model.ConsolidatedCity, college)


@colleges_module.bp.route(
    "/<string:public_id>/consolidated_cities", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_consolidated_cities(college):
    """Removes consolidated cities from college.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
        
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_location_requirement(
        consolidated_city_model.ConsolidatedCity, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_states_blacklist(college):
    """Gets college's states blacklist in database

    Retrieves paginated list of all college's states blacklist from database or 
    college's states blacklist that contains the search request parameter if 
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_locations_blacklist(
        state_model.State,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_states_blacklist(college):
    """adds states blacklist to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            States blacklist successfully added to college. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_locations_blacklist(state_model.State, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/states", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_states_blacklist(college):
    """Removes states blacklist from college.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
        
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_locations_blacklist(state_model.State, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_counties_blacklist(college):
    """Gets college's counties blacklist in database

    Retrieves paginated list of all college's counties blacklist from database or 
    college's counties blacklist that contains the search request parameter if 
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_locations_blacklist(
        county_model.County,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_counties_blacklist(college):
    """adds counties blacklist to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Counties blacklist successfully added to college. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_locations_blacklist(county_model.County, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/counties", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_counties_blacklist(college):
    """Removes counties blacklist from college.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
        
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_locations_blacklist(county_model.County, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_places_blacklist(college):
    """Gets college's places blacklist in database

    Retrieves paginated list of all college's places blacklist from database or 
    college's places blacklist that contains the search request parameter if 
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_locations_blacklist(
        place_model.Place,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_places_blacklist(college):
    """adds places blacklist to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Places blacklist successfully added to college. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_locations_blacklist(place_model.Place, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/places", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_places_blacklist(college):
    """Removes places blacklist from college.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
        
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_locations_blacklist(place_model.Place, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_college_consolidated_cities_blacklist(college):
    """Gets college's consolidated cities blacklist in database

    Retrieves paginated list of all college's consolidated cities blacklist 
    from database or college's consolidated cities blacklist that contains the 
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.get_locations_blacklist(
        consolidated_city_model.ConsolidatedCity,
        "colleges",
        "college",
        college,
        public_id=college.public_id)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_college_consolidated_cities_blacklist(college):
    """adds consolidated cities blacklist to college.

    POST:
        Params:
            public_id (string) (required): public id of college.

        Consumes:
            Application/json.
        
        Request Body:
            List of state FIPS.
        
        Example::
            ["FIPS 1", "FIPS 2"]
    
    Responses:
        201:
            Consolidated cities blacklist successfully added to college. 
            Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College not found, returns message.

            produces:
                Application/json.
        422:
            Some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    return utils.post_locations_blacklist(
        consolidated_city_model.ConsolidatedCity, college)


@colleges_module.bp.route(
    "/<string:public_id>/blacklist/consolidated_cities", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def delete_college_consolidated_cities_blacklist(college):
    """Removes consolidated cities blacklist from college.

    DELETE:
        Params:
            public_id (string) (required): public id of college.
        
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
            College not found, returns message.

            produces:
                Application/json.
    """
    return utils.delete_locations_blacklist(
        consolidated_city_model.ConsolidatedCity, college)


@colleges_module.bp.route("/majors_suggestions/<string:query>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def majors_suggestions(query):
    """Returns majors suggestions

    Retrieves majors suggestions where the major's name contains the query 
    keyword.

    GET:
        Params:
            query (string) (required): Query keyword.
    
    Responses:
        200:
            Returns majors list.

            Produces:
                Application/json.
    """
    suggestions = major_model.Major.query.filter(
        major_model.Major.name.like(f"%{query}%")).limit(5).all()

    return flask.jsonify([suggestion.to_dict() for suggestion in suggestions])


@colleges_module.bp.route("/<string:public_id/pictures")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def get_pictures(college):
    """Gets college's pictures in database

    Retrieves paginated list of all college's pictures from database.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of colleges.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of pictures],
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
            College not found, returns message.

            produces:
                Application/json.
    """
    resources = college.pictures.all()

    data = [item.to_dict() for item in resources]

    return flask.jsonify(data)


@colleges_module.bp.route("/<string:public_id>/pictures", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def post_picture(college):
    """Creates and adds picture to college.

    POST:
        Params:
            public_id (string) (required): public id of college.
        
        Consumes:
            image/png
            image/jpeg
        
        Request Body:
            Picture file
        
        Request Body:
            Dictionary of editable picture fields. name field is required.

        Consumes:
            Application/json.
        
        Example::
            {
                "name": "example picture name"
            }
    
    Responses:
        201:
            Scholarship successfully created and added to college. 
            Returns picture public id.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            College or file not found, returns message.

            produces:
                Application/json.
    """
    if "picture" not in flask.request.files:
        return flask.jsonify({"message": "file missing"}), 404

    filename = app.photos.save(flask.request.files["picture"])
    data = flask.request.get_json() or {}

    if "type" not in data:
        data["type"] = "campus"
    else:
        data["type"] = data["type"].lower()

    picture = picture_model.Picture(name=filename, college=college, **data)
    app.db.session.add(picture)
    app.db.session.commit()

    return flask.jsonify(picture.public_id)
