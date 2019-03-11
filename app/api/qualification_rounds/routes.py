import flask
import app
import marshmallow

from app.api import qualification_rounds as qualification_rounds_module
from app.models import qualification_round as qualification_round_model
from app.api import errors
from app.schemas import qualification_round_schema as qualification_round_schema_class
from app import security

qualification_round_schema = qualification_round_schema_class.QualificationRoundSchema(
)


@qualification_rounds_module.bp.route("/", strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_qualification_rounds():
    """Gets qualification_rounds in database

    Retrieves paginated list of all qualification_rounds from database or qualification_rounds that
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
            of qualification_rounds. See PaginatedAPIMixin.

            produces:
                Application/json.
    """

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = qualification_round_model.QualificationRound.query.filter(
            qualification_round_model.QualificationRound.name.like(
                f"%{search}%"))

        data = qualification_round_model.QualificationRound.to_collection_dict(
            query,
            page,
            per_page,
            "qualification_rounds.get_qualification_rounds",
            search=search)
    else:
        query = qualification_round_model.QualificationRound.query
        data = qualification_round_model.QualificationRound.to_collection_dict(
            query, page, per_page,
            "qualification_rounds.get_qualification_rounds")

    return flask.jsonify(data)


@qualification_rounds_module.bp.route(
    "/", strict_slashes=False, methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def create_qualification_round():
    """ Creates qualification_round

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
            Successfully created qualification_round. Returns link to get qualification_round.

            produces:
                Application/json.

            Example::
                {
                    "qualification_round": link to get qualification_round
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
        qualification_round_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    qualification_round = qualification_round_model.QualificationRound.first(
        name=data["name"])

    if qualification_round is not None:
        return errors.bad_request(
            f"qualification_round '{data['name']}' already exists")

    qualification_round = qualification_round_model.QualificationRound(**data)

    app.db.session.add(qualification_round)
    app.db.session.commit()

    return flask.jsonify({
        "qualification_round":
        flask.url_for(
            "qualification_rounds.get_qualification_round",
            id=qualification_round.id)
    }), 201


@qualification_rounds_module.bp.route("/<int:id>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_qualification_round(id):
    """Gets qualification_round.

    Retrieves single qualification_round from database.

    GET:
        Params:
            name (string) (required): qualification_round name.

    Responses:
        200:
            Successfully retrieves qualification_round. Returns qualification_round.

            produces:
                Application/json.

        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    qualification_round = qualification_round_model.QualificationRound.query.get_or_404(
        id)

    return flask.jsonify(qualification_round.to_dict())


@qualification_rounds_module.bp.route("/<int:id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def delete_qualification_round(id):
    """Deletes qualification_round.

    Deletes qualification_round from database.

    DELETE:
        Params:
            name (string) (required): name of qualification_round.

    Responses:
        200:
            QualificationRound successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            QualificationRound not found, returns message.

            produces:
                Application/json.
    """
    qualification_round = qualification_round_model.QualificationRound.query.get_or_404(
        id)

    app.db.session.delete(qualification_round)
    app.db.session.commit()

    return flask.jsonify({"message": "qualification_round deleted"})


@qualification_rounds_module.bp.route("/<int:id>/programs")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_programs(id):
    """Retrieves programs that has this qualification_round.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults
            to one.
            per_page (int) (optional): Number of items to retrieve per page,
            defaults to configuration constant PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".

    Responses:
        200:
            Paginated list of programs.

            Produces:
                Application/json.
        404:
            QualificationRound not found, returns message.

            produces:
                Application/json.
    """
    qualification_round = qualification_round_model.QualificationRound.query.get_or_404(
        id)

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    return flask.jsonify(
        qualification_round_model.QualificationRound.to_collection_dict(
            qualification_round.programs,
            page,
            per_page,
            "qualification_rounds.get_programs",
            id=id))
