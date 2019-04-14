#TODO: use common errors from errors module
#TODO: remove get_entity and use first_or_404 or get_or_404
import flask
import marshmallow

import app
import re
from app.api import colleges as colleges_module
from app import security, utils
from app.models import college as college_model
from app.models import college_details as college_details_model
from app.models import major as major_model
from app.models import detail as detail_model
from app.models import location as location_model
from app.schemas import college_schema as college_schema_class
from app.schemas import detail_schema as detail_schema_class
from app.api import errors

college_schema = college_schema_class.CollegeSchema()
detail_schema = detail_schema_class.DetailSchema()


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
            of colleges. See PaginatedAPIMixin.

            produces:
                Application/json.
    """
    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["COLLEGES_PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = college_model.College.query.join(
            college_details_model.CollegeDetails,
            college_details_model.CollegeDetails.id == college_model.College.
            id,
            isouter=True).filter(
                college_details_model.CollegeDetails.name.like(f"%{search}%"))

        data = college_model.College.to_collection_dict(
            query, page, per_page, "colleges.get_colleges", search=search)
    else:
        query = college_model.College.query
        data = college_model.College.to_collection_dict(
            query, page, per_page, "colleges.get_colleges")

    return flask.jsonify(data)


@colleges_module.bp.route("/", methods=["POST"], strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def post_college():
    """Creates college.

    Creates, validates and adds college to database.

    Post:
        Consumes:
            Application/json.
        Request body:
            dictionary with the a name attribute.
        
            Example::
                {
                    "name": "example name"
                }
    Responses:
        201:
            Successfully created college. Returns link to get college.

            produces:
                Application/json.

            Example::
                {
                    "college": link to get college
                }
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        400:
            some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        college_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    college_details = college_details_model.CollegeDetails(**data)
    college = college_model.College(college_details=college_details)
    app.db.session.add(college_details)
    app.db.session.add(college)
    app.db.session.commit()

    return flask.jsonify({
        "college":
        flask.url_for("colleges.get_college", id=college.id)
    }), 201


@colleges_module.bp.route("/<int:id>", methods=["GET"])
# @security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College)
def get_college(college):
    """Gets college.

    Retrieves single college from database.

    GET:
        Params:
            name (string) (required): college name.
    
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


@colleges_module.bp.route("/<int:id>", methods=["PATCH"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College)
def patch_college(college):
    """Edits college.

    PATCH:
        Params:
            name (string) (required): name of college.

        Consumes:
            Application/json.
        
        Request Body:
            Dictionary of college fields.
        
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
        400:
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
        return flask.jsonify(err.messages), 400

    college_details = college.college_details
    college_details.update(data)
    app.db.session.commit()
    return flask.jsonify({
        "college":
        flask.url_for("colleges.get_college", id=college.id)
    })


@colleges_module.bp.route("/<int:id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College)
def delete_college(college):
    """Deletes college.

    Deletes college from database.

    DELETE:
        Params:
            name (string) (required): name of college.
    
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
    app.db.session.delete(college)
    app.db.session.commit()

    return flask.jsonify({"message": "college deleted"})


# add majors
@colleges_module.bp.route("/<int:id>/majors", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def add_majors(id):
    """Adds majors to college

    POST:
        params:
            id (int): college id.
        
        Request body:
            list of majors id.

            consumes:
                application/json.
    
    Returns:
        200:
            link to get college majors.

            produces:
                application/json.
        404:
            no college found

            produces:
                application/json.
    """
    data = flask.request.get_json()

    if not data:
        return errors.bad_request("no data provided")

    college = college_model.College.query.get_or_404(id)

    for major_id in data:
        major = major_model.Major.get(major_id)

        if major is not None:
            college.add_major(major)

    return flask.jsonify({
        "majors": flask.url_for("colleges.get_majors", id=id)
    })


# read majors
@colleges_module.bp.route("/<int:id>/majors")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_majors(id):
    """Gets college majors in database

    Retrieves paginated list of all college majors from database.

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
            of colleges. See PaginatedAPIMixin.

            produces:
                Application/json.
    """
    college = college_model.College.query.get_or_404(id)

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    return flask.jsonify(
        major_model.Major.to_collection_dict(
            college.majors, page, per_page, "colleges.get_majors", id=id))


# remove majors
@colleges_module.bp.route("/<int:id>/majors", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def remove_majors(id):
    """removes majors to college

    DELETE:
        params:
            id (int): college id.
        
        Request body:
            list of majors id.

            consumes:
                application/json.
    
    Returns:
        200:
            link to get college majors.

            produces:
                application/json.
        404:
            no college found

            produces:
                application/json.
    """
    data = flask.request.get_json()

    if not data:
        return errors.bad_request("no data provided")

    college = college_model.College.query.get_or_404(id)

    for major_id in data:
        major = major_model.Major.get(major_id)

        if major is not None:
            college.remove_major(major)

    return flask.jsonify({
        "majors": flask.url_for("colleges.get_majors", id=id)
    })


@colleges_module.bp.route("/<int:id>/additional_details")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_college_additional_details(id):
    """Gets college additional details.

    GET:
        Param Args:
            id (integer): college id.
    Responses:
        200:
            Successfully retieves college additional details.

            produces:
                Application/json.
        
        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    college = college_model.College.query.get_or_404(id)

    return flask.jsonify(college.get_additional_details())


@colleges_module.bp.route("/<int:id>/additional_details", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def post_college_additional_details(id):
    """Adds college addtional detail.

    Post:
        Consumes:
            Application/json.
        Request body:
            dictionary with name, type and value required. type should be 
            "integer", "decimal", "string", "boolean".
        
            Example::
                {
                    "name": "act",
                    "type": "integer",
                    "value": "1"
                }
    Responses:
        201:
            Successfully created and added college additional detail. Returns 
            link to get college additional details.

            produces:
                Application/json.

            Example::
                {
                    "additional_details": link to get college additional 
                        details.
                }
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        400:
            some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return errors.bad_request("no data provided")

    college: college_model.College = college_model.College.query.get_or_404(id)

    try:
        detail_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    if not detail_model.Detail.validate_value(data["value"], data["type"]):
        return errors.bad_request("value does not match type")

    detail = detail_model.Detail(**data)

    app.db.session.add(detail)
    college.add_additional_detail(detail)

    app.db.session.commit()

    return flask.jsonify({
        "additional_details":
        flask.url_for("colleges.get_college_additional_details", id=id)
    }), 201


@colleges_module.bp.route(
    "/<int:college_id>/additional_details/<int:detail_id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def delete_college_additional_details(college_id, detail_id):
    """Adds college addtional detail.

    Post:
        Param Args:
            college_id (integer): college id.
            detail_id (integer): detail id.

    Responses:
        200:
            Successfully removed additional detail from college. Returns link 
            to get college additional details.

            produces:
                Application/json.

            Example::
                {
                    "additional_details": link to get college additional 
                        details.
                }
    """
    college = college_model.College.query.get_or_404(college_id)

    detail = detail_model.Detail.query.get_or_404(detail_id)

    college.remove_additional_detail(detail)
    app.db.session.delete(detail)
    app.db.session.commit()

    return flask.jsonify({
        "additional_details":
        flask.url_for(
            "colleges.get_college_additional_details", id=college_id)
    })


@colleges_module.bp.route("/<int:id>/grade_requirement_groups")
def get_grade_requirement_groups(id):
    """
    Gets grade requirement groups from college.
    GET:
       Args:
            id (integer): college id.
    Responses:
        200:
            returns list of grade requirement groups.

            Produces:
                Application/json.

        404:
            college not found.

            Produces:
                Application/json.
    """

    college = college_model.College.query.get_or_404(id)

    return flask.jsonify(
        [group.to_dict() for group in college.grade_requirement_groups.all()])


@colleges_module.bp.route(
    "/<int:id>/grade_requirement_groups", methods=["POST"])
def post_grade_requirement_group(id):
    """creates college grade requirement group.

    POST:
        Args:
            id (integer): college id.

    Responses:
        200:
            returns grade requirement group.

            Produces:
                Application/json.

        404:
            college not found.

            Produces:
                Application/json.
    """
    college = college_model.College.query.get_or_404(id)
    group = college.create_grade_requirement_group()
    app.db.session.commit()
    return flask.jsonify(group.to_dict()), 201


@colleges_module.bp.route(
    "/<int:college_id>/grade_requirement_groups/<int:group_id>",
    methods=["DELETE"])
def delete_grade_requirement_group(college_id, group_id):
    """Deletes college grade requirement group.

    POST:
        Args:
            id (integer): college id.

    Responses:
        200:
            returns list of grade requirement group.

            Produces:
                Application/json.

        404:
            college not found.

            Produces:
                Application/json.
    """
    college = college_model.College.query.get_or_404(college_id)
    group = college.grade_requirement_groups.filter_by(id=group_id).first()

    if group is None:
        return errors.not_found("college doesn't have grade "
                                f"requirement group with id {group_id}")
    college.delete_grade_requirement_group(group)
    app.db.session.commit()

    return flask.jsonify({
        "get_grade_requirement_groups":
        flask.url_for("colleges.get_grade_requirement_groups", id=college_id)
    })


@colleges_module.bp.route("/<int:id>/location_requirements", methods=["POST"])
def add_location_requirement(id):
    """
    Adds location requirement to the college's location requirements.

    POST:
        Args:
            id (integer): college id.
        
        Consumes:
            Application/json.
        
        Request Body:
            location requirement dict.

            Example::

                {
                    "state": state,
                    "county": county,
                    "place": place,
                    "zip_code": zip_code
                    "blacklist": 1 or 0
                }
        
    Responses:

        200:
            Successfully adds location requirement.
    """

    data = flask.request.get_json() or {}

    if not data or not isinstance(data, dict):
        return errors.bad_request("no data provided or bad structure")

    try:
        state = data["state"]
        county = data["county"]
        place = data["place"]
        zip_code = data["zip_code"]
        blacklist = data["blacklist"]

    except KeyError:
        return errors.bad_request("missing fields")

    if place is not None and (county is None or state is None):
        return errors.bad_request(
            "if place is defined, county and state must be defined")

    if county is not None and state is None:
        return errors.bad_request(
            "if county is defined, state must be defined")

    if zip_code is None and state is None:
        return errors.bad_request("zip code or state must be defined")

    if blacklist not in [1, 0]:
        return errors.bad_request("blacklist must be either 1 or 0")

    blacklist = blacklist == 1

    college = college_model.College.query.get_or_404(id)

    if zip_code is not None:

        if not re.fullmatch(r"[0-9]{5}(?:-[0-9]{4})?", zip_code):
            return errors.bad_request("invalid zip code")

        location = location_model.Location(
            zip_code=zip_code, blacklist=blacklist)

    else:
        location = location_model.Location(
            state=state, county=county, place=place, blacklist=blacklist)

    app.db.session.add(location)

    college.add_location_requirement(location)

    app.db.session.commit()

    return flask.jsonify({
        "location_requirements":
        flask.url_for("colleges.get_location_requirements", id=id)
    }), 201


@colleges_module.bp.route(
    "/<int:college_id>/location_requirements/<int:location_id>",
    methods=["DELETE"])
def delete_location_requirement(college_id, location_id):
    """
    Deletes location requirement from college.

    DELETE:
        Args:
            college_id (integer): college id.
            location_id (integer): location id.
    Responses:
        200:
            location removed successfully.

            Produces:
                Application/json.
        404:
            college not found or college does not have location requirement.

            Produces:
                Application/json.
    """

    college = college_model.College.query.get_or_404(college_id)
    location = college.location_requirements.filter_by(id=location_id).first()

    if location is None:
        return errors.not_found("college doesn't have location requirement")

    college.remove_location_requirement(location)

    db.session.delete(location)
    db.session.commit()


@colleges_module.bp.route("/<int:id>/location_requirements")
def get_location_requirements(id):
    """
    Gets location requirements.

    GET:
        id (integer): college id.
    Responses:
        200:
            Gets list of location requirements.

            Produces:
                Application/json.

        404:
            college not found.

            Produces:
                Application/json.
    """

    college = college_model.College.query.get_or_404(id)
    accepted_locations = college.location_requirements.filter_by(
        blacklist=False).all()
    blacklisted_locations = college.location_requirements.filter_by(
        blacklist=True).all()

    return flask.jsonify({
        "accepted": [location.to_dict() for location in accepted_locations],
        "blacklisted":
        [location.to_dict() for location in blacklisted_locations],
    })