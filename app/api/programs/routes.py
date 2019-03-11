import flask
import app
import marshmallow

from app.api import programs as programs_module
from app.models import program as program_model
from app.models import qualification_round as qualification_round_model
from app.api import errors
from app.schemas import program_schema as program_schema_class
from app import security

program_schema = program_schema_class.ProgramSchema()


@programs_module.bp.route("/", strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_programs():
    """Gets programs in database

    Retrieves paginated list of all programs from database or programs that
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
            of programs. See PaginatedAPIMixin.

            produces:
                Application/json.
    """

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = program_model.Program.query.filter(
            program_model.Program.name.like(f"%{search}%"))

        data = program_model.Program.to_collection_dict(
            query, page, per_page, "programs.get_programs", search=search)
    else:
        query = program_model.Program.query
        data = program_model.Program.to_collection_dict(
            query, page, per_page, "programs.get_programs")

    return flask.jsonify(data)


@programs_module.bp.route("/", strict_slashes=False, methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def create_program():
    """ Creates program

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
            Successfully created program. Returns link to get program.

            produces:
                Application/json.

            Example::
                {
                    "program": link to get program
                }
        400:
            bad request. Returns message "no data provided" or invalid fields

            produces:
                Application/json.
    """

    data = flask.request.get_json() or {}

    if not data:
        return errors.bad_request("no data provided")

    try:
        program_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    program = program_model.Program.first(name=data["name"])

    if program is not None:
        return errors.bad_request(f"program '{data['name']}' already exists")

    program = program_model.Program(**data)

    app.db.session.add(program)
    app.db.session.commit()

    return flask.jsonify({
        "program":
        flask.url_for("programs.get_program", id=program.id)
    }), 201


@programs_module.bp.route("/<int:id>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_program(id):
    """Gets program.

    Retrieves single program from database.

    GET:
        Params:
            name (string) (required): program name.

    Responses:
        200:
            Successfully retrieves program. Returns program.

            produces:
                Application/json.

        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    program = program_model.Program.query.get_or_404(id)

    return flask.jsonify(program.to_dict())


@programs_module.bp.route("/<int:id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def delete_program(id):
    """Deletes program.

    Deletes program from database.

    DELETE:
        Params:
            name (string) (required): name of program.

    Responses:
        200:
            Program successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            Program not found, returns message.

            produces:
                Application/json.
    """
    program = program_model.Program.query.get_or_404(id)

    app.db.session.delete(program)
    app.db.session.commit()

    return flask.jsonify({"message": "program deleted"})


# add qualification_rounds
@programs_module.bp.route("/<int:id>/qualification_rounds", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def add_qualification_rounds(id):
    """Adds qualification_rounds to program

    POST:
        params:
            id (int): program id.

        Request body:
            list of qualification_rounds id.

            consumes:
                application/json.

    Returns:
        200:
            link to get program qualification_rounds.

            produces:
                application/json.
        404:
            no program found

            produces:
                application/json.
    """
    data = flask.request.get_json()

    if not data:
        return errors.bad_request("no data provided")

    program = program_model.Program.query.get_or_404(id)

    for qualification_round_id in data:
        qualification_round = qualification_round_model.QualificationRound.get(qualification_round_id)

        if qualification_round is not None:
            program.add_qualification_round(qualification_round)

    return flask.jsonify({
        "qualification_rounds": flask.url_for("programs.get_qualification_rounds", id=id)
    })


# read qualification_rounds
@programs_module.bp.route("/<int:id>/qualification_rounds")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_qualification_rounds(id):
    """Gets program qualification_rounds in database

    Retrieves paginated list of all program qualification_rounds from database.

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
            of programs. See PaginatedAPIMixin.

            produces:
                Application/json.
    """
    program = program_model.Program.query.get_or_404(id)

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    return flask.jsonify(
        qualification_round_model.QualificationRound.to_collection_dict(
            program.qualification_rounds, page, per_page, "programs.get_qualification_rounds", id=id))


# remove qualification_rounds
@programs_module.bp.route("/<int:id>/qualification_rounds", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def remove_qualification_rounds(id):
    """removes qualification_rounds to program

    DELETE:
        params:
            id (int): program id.

        Request body:
            list of qualification_rounds id.

            consumes:
                application/json.

    Returns:
        200:
            link to get program qualification_rounds.

            produces:
                application/json.
        404:
            no program found

            produces:
                application/json.
    """
    data = flask.request.get_json()

    if not data:
        return errors.bad_request("no data provided")

    program = program_model.Program.query.get_or_404(id)

    for qualification_round_id in data:
        qualification_round = qualification_round_model.QualificationRound.get(qualification_round_id)

        if qualification_round is not None:
            program.remove_qualification_round(qualification_round)

    return flask.jsonify({
        "qualification_rounds": flask.url_for("programs.get_qualification_rounds", id=id)
    })
