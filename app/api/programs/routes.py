import flask
import app
import marshmallow

from app import utils
from app.api import programs as programs_module
from app.models import program as program_model
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
        data = program_model.Program.to_collection_dict(query, page, per_page,
                                                    "programs.get_programs")

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
            bad rquest. Returns message "no data provided" or invalid fields

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
            Successfully retieves program. Returns program.

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
    college = program_model.Program.query.get_or_404(id)

    app.db.session.delete(college)
    app.db.session.commit()

    return flask.jsonify({"message": "college deleted"})


# @programs_module.bp.route("/<int:id>/colleges")
# @security.user_role([security.ADMINISTRATOR, security.BASIC])
# def get_colleges(id):
#     """Retrieves colleges that has this program.
#
#     GET:
#         Request params:
#             page (int) (optional): Page number in paginated resource, defaults
#             to one.
#             per_page (int) (optional): Number of items to retrieve per page,
#             defaults to configuration constant PER_PAGE.
#             search (string) (optional): Search query keyword, defaults to "".
#
#     Responses:
#         200:
#             Paginated list of colleges.
#
#             Produces:
#                 Application/json.
#         404:
#             Program not found, returns message.
#
#             produces:
#                 Application/json.
#     """
#     program = program_model.Program.query.get_or_404(id)
#
#     page = flask.request.args.get("page", 1, type=int)
#     per_page = flask.request.args.get(
#         "per_page", flask.current_app.config["PER_PAGE"], type=int)
#
#     return flask.jsonify(
#         program_model.Program.to_collection_dict(
#             program.colleges, page, per_page, "programs.get_colleges", id=id))
