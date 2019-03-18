import flask
import marshmallow

import app
from app.api import scholarships as scholarships_module
from app import security
from app.models import scholarship as scholarship_model
from app.models import scholarship_details as scholarship_details_model
from app.models import detail as detail_model
from app.models import association_tables
from app.models import program as program_model
from app.models import qualification_round as qualification_round_model
from app.schemas import scholarship_schema as scholarship_schema_class
from app.schemas import detail_schema as detail_schema_class
from app.api import errors
from app.models import college as college_model

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

    college_id = flask.request.args.get("college_id", type=int)

    if college_id is None:
        return errors.bad_request("no college provided")

    try:
        scholarship_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    college = college_model.College.query.get_or_404(college_id)

    scholarship_details = scholarship_details_model.ScholarshipDetails(**data)
    scholarship = scholarship_model.Scholarship(
        scholarship_details=scholarship_details, college=college)
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


@scholarships_module.bp.route("/<string:id>/scholarships_needed")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_scholarships_needed(id):
    """Gets scholarships needed for scholarship.

    Retrieves paginated list of all scholarships from database or scholarships
    that contains the search request parameter if defined.

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
    scholarship = scholarship_model.Scholarship.query.get_or_404(id)
    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page",
        flask.current_app.config["SCHOLARSHIPS_PER_PAGE"],
        type=int)
    search = flask.request.args.get("search", "", type=str)

    if search:
        query = scholarship.scholarships_needed.query.join(
            scholarship_details_model.ScholarshipDetails,
            scholarship_details_model.ScholarshipDetails.id == scholarship.
            scholarships_needed.id,
            isouter=True).filter(
                scholarship_details_model.ScholarshipDetails.name.like(
                    f"%{search}%"))

        data = scholarship.scholarships_needed.to_collection_dict(
            query,
            page,
            per_page,
            "scholarships.get_scholarships",
            search=search)
    else:
        query = scholarship.scholarships_needed
        data = scholarship_model.Scholarship.to_collection_dict(
            query, page, per_page, "scholarships.get_scholarships")

    return flask.jsonify(data)


@scholarships_module.bp.route(
    "/<string:id>/scholarships_needed", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def post_scholarships_needed(id):
    """adds scholarship needed to scholarship.

    POST:
        Params:
            id (string) (required): id of scholarship.

        Consumes:
            Application/json.

        Request Body:
            list of scholarships ids.

        Example::
            ["id 1", "id 2"]

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
    scholarship = scholarship_model.Scholarship.query.get_or_404(id)
    data = flask.request.get_json() or {}

    if not data or not isinstance(data, list):
        return errors.bad_request("no data provided")

    college = scholarship.college

    for scholarship_needed in data:
        if scholarship_needed == scholarship.id:
            continue

        scholarship_to_add = college.scholarships.filter_by(
            id=scholarship_needed).first()

        if scholarship_to_add is not None:
            scholarship.add_needed_scholarship(scholarship_to_add)

    app.db.session.commit()
    return flask.jsonify({
        "scholarships_needed":
        flask.url_for("scholarships.get_scholarships_needed", id=id)
    })


@scholarships_module.bp.route(
    "/<string:id>/scholarships_needed", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def delete_scholarships_needed(id):
    """removes scholarship needed to scholarship.

    POST:
        Params:
            id (string) (required): id of scholarship.

        Consumes:
            Application/json.

        Request Body:
            list of scholarships ids.

        Example::
            ["id 1", "id 2"]

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
    scholarship = scholarship_model.Scholarship.query.get_or_404(id)
    data = flask.request.get_json() or {}

    if not data or not isinstance(data, list):
        return errors.bad_request("no data provided")

    for scholarship_needed in data:
        scholarship_to_remove = scholarship.scholarships_needed.filter_by(
            id=scholarship_needed).first()

        if scholarship_to_remove is not None:
            scholarship.remove_needed_scholarship(scholarship_to_remove)

    app.db.session.commit()
    return flask.jsonify({
        "scholarships_needed":
        flask.url_for("scholarships.get_scholarships_needed", id=id)
    })


# TODO: Add common methods for adding removing and checking existence for
#   programs requirements and programs requirements qualification rounds.
@scholarships_module.bp.route(
    "/<int:id>/programs_requirement", methods=["POST"])
def add_programs_requirement(id):
    """Adds programs requirement to scholarship

    POST:
        Args:
            id (integer): scholarship id.

        Consumes:
            Application/json.

        Request Body:
            programs and qualification rounds needed for scholarship.

        Example::
            [
                {
                    "program_id": program id,
                    "qualification_rounds": [
                        qualification round id,
                        .
                        .
                        .
                    ]
                },
                .
                .
                .
            ]

    Responses:
        404:
            returns message if any model instance is not found.
        400:
            if data is empty, not a list or not well structured.
        200:
            success message.
    """
    data = flask.request.get_json() or {}

    if not data or not isinstance(data, list):
        return errors.bad_request("no data provided")

    scholarship = scholarship_model.Scholarship.query.get_or_404(id)

    try:
        for requirement in data:
            program_id = int(requirement["program_id"])
            program = program_model.Program.query.get_or_404(program_id)

            program_requirement = scholarship.programs_requirement.filter_by(
                program=program).first()

            if program_requirement is None:
                program_requirement = association_tables.ProgramRequirement(
                    program=program)
                app.db.session.add(program_requirement)
                scholarship.programs_requirement.append(program_requirement)

            for qualification_round_id in requirement["qualification_rounds"]:
                qualification_round_id = int(qualification_round_id)
                qualification_round = qualification_round_model \
                    .QualificationRound.query.get_or_404(
                        qualification_round_id)

                qualification_rounds_count = program_requirement.qualification_rounds.filter_by(
                    id=qualification_round_id).count()

                if qualification_rounds_count == 0:
                    program_requirement.qualification_rounds.append(
                        qualification_round)
    except KeyError:
        return errors.bad_request("missing fields in data provided")
    except ValueError:
        return errors.bad_request("invalid id")

    app.db.session.commit()

    return flask.jsonify({"message": "requirements added"})


@scholarships_module.bp.route("/<int:scholarship_id>/programs_requirement"
                              "/<int:program_id>/qualification_rounds",
                              methods=["POST"])
def add_qualification_rounds_to_program_requirement(scholarship_id,
                                                    program_id):
    """Adds qualification rounds to program_requirement

    POST:
        Args:
            scholarship_id (integer): scholarship id.
            program_id (integer): program id of program requirement.
        Consumes:
            Application/json.
        Request body:
            [qualification round id, ...]
    Responses:
    200:
        qualification rounds added to scholarship program requirement

        Produces:
            Application/json.
    400:
        no data provided or data not list, invalid qualification round id

        Produces:
            Application/json.
    404:
        either scholarship or program not found, or program doesn't have a
        qualification round

        Produces:
            Application/json.
    """
    data = flask.request.get_json() or {}

    if not data or not isinstance(data, list):
        return errors.bad_request("no data provided or bad structure")

    scholarship = scholarship_model.Scholarship.query.get_or_404(
        scholarship_id)

    program_requirement = scholarship.programs_requirement.filter(
        program_model.Program.id == program_id).first_or_404()

    for qualification_round_id in data:

        try:
            qualification_round_id = int(qualification_round_id)
        except ValueError:
            return errors.bad_request("invalid qualification round id")

        qualification_round = program_requirement.program.qualification_rounds \
            .filter_by(id=qualification_round_id).first()

        if qualification_round is None:
            return errors.not_found("program does not have qualification "
                                    f"round {qualification_round_id}")

        qualification_rounds_with_id_count = program_requirement \
            .qualification_rounds.filter_by(id=qualification_round_id).count()

        if qualification_rounds_with_id_count == 0:
            program_requirement.qualification_rounds.append(
                qualification_round)

    app.db.session.commit()

    return flask.jsonify({"message": "qualification rounds added"})
