#TODO: use common errors from errors module
import flask
import marshmallow

import app
from app.api import colleges as colleges_module
from app import security, utils
from app.models import college as college_model
from app.models import college_details as college_details_model
from app.schemas import college_schema

college_schema = college_schema.CollegeSchema()


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
        college_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 422

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
@security.user_role([security.ADMINISTRATOR, security.BASIC])
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