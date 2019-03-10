import flask
import marshmallow

import app
from app.api import scholarships as scholarships_module
from app import security
from app.models import scholarship as scholarship_model
from app.models import scholarship_details as scholarship_details_model
from app.models import detail as detail_model
from app.schemas import scholarship_schema as scholarship_schema_class
from app.schemas import detail_schema as detail_schema_class
from app.api import errors

scholarship_schema = scholarship_schema_class.ScholarshipSchema()
detail_schema = detail_schema_class.DetailSchema()


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
            defaults to configuration constant SCHOLARSHIP_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".

    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of scholarships. See PaginatedAPIMixin.

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
        query = scholarship_model.Scholarship.query.join(
            scholarship_details_model.ScholarshipDetails,
            scholarship_details_model.ScholarshipDetails.id ==
            scholarship_model.Scholarship.id,
            isouter=True).filter(
                scholarship_details_model.ScholarshipDetails.name.like(
                    f"%{search}%"))

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


@scholarships_module.bp.route("/", methods=["POST"], strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def post_scholarship():
    """Creates scholarship.

    Creates, validates and adds scholarship to database.

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
            Successfully created scholarship. Returns link to get scholarship.

            produces:
                Application/json.

            Example::
                {
                    "scholarship": link to get scholarship
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

    try:
        scholarship_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    scholarship_details = scholarship_details_model.ScholarshipDetails(**data)
    scholarship = scholarship_model.Scholarship(
        scholarship_details=scholarship_details)
    app.db.session.add(scholarship_details)
    app.db.session.add(scholarship)
    app.db.session.commit()

    return flask.jsonify({
        "scholarship":
        flask.url_for("scholarships.get_scholarship", id=scholarship.id)
    }), 201


@scholarships_module.bp.route("/<int:id>", methods=["GET"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_scholarship(id):
    """Gets scholarship.

    Retrieves single scholarship from database.

    GET:
        Params:
            name (string) (required): scholarship name.

    Responses:
        200:
            Successfully retrieves scholarship. Returns scholarship.

            produces:
                Application/json.

        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    scholarship = scholarship_model.Scholarship.query.get_or_404(id)
    return flask.jsonify(scholarship.to_dict())


@scholarships_module.bp.route("/<int:id>", methods=["PATCH"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def patch_scholarship(id):
    """Edits scholarship.

    PATCH:
        Params:
            name (string) (required): name of scholarship.

        Consumes:
            Application/json.

        Request Body:
            Dictionary of scholarship fields.

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
        400:
            some or all of the fields are invalid. Returns error of
            invalid fields.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return errors.bad_request("no data provided")

    scholarship = scholarship_model.Scholarship.query.get_or_404(id)

    try:
        scholarship_schema.load(data, partial=True)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    scholarship_details = scholarship.scholarship_details
    scholarship_details.update(data)
    app.db.session.commit()
    return flask.jsonify({
        "scholarship":
        flask.url_for("scholarships.get_scholarship", id=scholarship.id)
    })


@scholarships_module.bp.route("/<int:id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def delete_scholarship(id):
    """Deletes scholarship.

    Deletes scholarship from database.

    DELETE:
        Params:
            name (string) (required): name of scholarship.

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
    scholarship = scholarship_model.Scholarship.query.get_or_404(id)

    app.db.session.delete(scholarship)
    app.db.session.commit()

    return flask.jsonify({"message": "scholarship deleted"})


@scholarships_module.bp.route("/<int:id>/additional_details")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_scholarship_additional_details(id):
    """Gets scholarship additional details.

    GET:
        Param Args:
            id (integer): scholarship id.
    Responses:
        200:
            Successfully retrieves scholarship additional details.

            produces:
                Application/json.

        404:
            Scholarship not found, returns message.

            produces:
                Application/json.
    """
    scholarship = scholarship_model.Scholarship.query.get_or_404(id)

    return flask.jsonify(scholarship.get_additional_details())


@scholarships_module.bp.route("/<int:id>/additional_details", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def post_scholarship_additional_details(id):
    """Adds scholarship additional detail.

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
            Successfully created and added scholarship additional detail. Returns
            link to get scholarship additional details.

            produces:
                Application/json.

            Example::
                {
                    "additional_details": link to get scholarship additional
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

    scholarship = scholarship_model.Scholarship.query.get_or_404(id)

    try:
        detail_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    if not detail_model.Detail.validate_value(data["value"], data["type"]):
        return errors.bad_request("value does not match type")

    detail = detail_model.Detail(**data)

    app.db.session.add(detail)
    scholarship.add_additional_detail(detail)

    app.db.session.commit()

    return flask.jsonify({
        "additional_details":
        flask.url_for(
            "scholarships.get_scholarship_additional_details", id=id)
    }), 201


@scholarships_module.bp.route(
    "/<int:scholarship_id>/additional_details/<int:detail_id>",
    methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def delete_scholarship_additional_details(scholarship_id, detail_id):
    """Adds scholarship additional detail.

    Post:
        Param Args:
            scholarship_id (integer): scholarship id.
            detail_id (integer): detail id.

    Responses:
        200:
            Successfully removed additional detail from scholarship. Returns link
            to get scholarship additional details.

            produces:
                Application/json.

            Example::
                {
                    "additional_details": link to get scholarship additional
                        details.
                }
    """
    scholarship = scholarship_model.Scholarship.query.get_or_404(
        scholarship_id)

    detail = detail_model.Detail.query.get_or_404(detail_id)

    scholarship.remove_additional_detail(detail)
    app.db.session.delete(detail)
    app.db.session.commit()

    return flask.jsonify({
        "additional_details":
        flask.url_for(
            "scholarships.get_scholarship_additional_details",
            id=scholarship_id)
    })
