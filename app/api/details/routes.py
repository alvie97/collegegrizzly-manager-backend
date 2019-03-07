#TODO: Get detail colleges.
import flask
import marshmallow

import app
from app.api import details as details_module
from app.api import errors
from app.models import detail as detail_model
from app.schemas import detail_schema as detail_schema_class
from app import security

detail_schema = detail_schema_class.DetailSchema()


@details_module.bp.route("/", strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_details():
    """Gets details in database

    Retrieves paginated list of all details from database or details that 
    contains the search request parameter if defined.

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
            of details. See PaginatedAPIMixin.

            produces:
                Application/json.
    """

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = detail_model.Detail.query.filter(
            detail_model.Detail.name.like(f"%{search}%"))

        data = detail_model.Detail.to_collection_dict(
            query, page, per_page, "details.get_details", search=search)
    else:
        query = detail_model.Detail.query
        data = detail_model.Detail.to_collection_dict(query, page, per_page,
                                                      "details.get_details")

    return flask.jsonify(data)


@details_module.bp.route("/<int:id>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_detail(id):
    """Gets detail.

    Retrieves single detail from database.

    GET:
        Params:
            name (string) (required): detail name.
    
    Responses:
        200:
            Successfully retieves detail. Returns detail.

            produces:
                Application/json.
        
        404:
            Detail not found, returns message.

            produces:
                Application/json.
    """
    detail = detail_model.Detail.query.get_or_404(id)

    return flask.jsonify(detail.to_dict())


@details_module.bp.route("/<int:id>", methods=["PATCH"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def patch_detail(id):
    """Edits detail.

    PATCH:
        Params:
            name (string) (required): name of detail.

        Consumes:
            Application/json.
        
        Request Body:
            Dictionary of detail fields.
        
        Example::
            {
                "name": "example detail name"
            }
    
    Responses:
        200:
            Detail successfully modified. Returns link to detail.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Detail not found, returns message.

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

    detail = detail_model.Detail.query.get_or_404(id)

    try:
        detail_schema.load(data, partial=True)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    if "type" in data:
        if "value" in data:
            if not detail_model.Detail.validate_value(data["value"],
                                                      data["type"]):
                return errors.bad_request(
                    f"value is not of type {data['type']}")
        else:
            if not detail_model.Detail.validate_value(detail.value,
                                                      data["type"]):
                return errors.bad_request(
                    f"value is not of type {data['type']}")
    elif "value" in data:
        if not detail_model.Detail.validate_value(data["value"], detail.type):
            return errors.bad_request(f"value is not of type {detail.type}")

    detail.update(data)
    app.db.session.commit()

    return flask.jsonify({
        "detail": flask.url_for("details.get_detail", id=id)
    })


@details_module.bp.route("/<int:id>/college")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_college(id):
    """Retrieves college that owns this detail.

    GET:
    Responses:
        200:
            retrieves college.

            Produces:
                Application/json.
        404:
            Detail not found, returns message.

            produces:
                Application/json.
    """
    detail = detail_model.Detail.query.get_or_404(id)
    return flask.jsonify(detail.college.to_dict())