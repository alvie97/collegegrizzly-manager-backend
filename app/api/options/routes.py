import flask
import app
import marshmallow

from app.api import options as options_module
from app.models import option as option_model
from app.api import errors
from app.schemas import option_schema as option_schema_class
from app import security

option_schema = option_schema_class.OptionSchema()


@options_module.bp.route("/", strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_options():
    """Gets options in database

    Retrieves paginated list of all options from database or options that
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
            of options. See PaginatedAPIMixin.

            produces:
                Application/json.
    """

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = option_model.Option.query.filter(
            option_model.Option.name.like(f"%{search}%"))

        data = option_model.Option.to_collection_dict(
            query, page, per_page, "options.get_options", search=search)
    else:
        query = option_model.Option.query
        data = option_model.Option.to_collection_dict(query, page, per_page,
                                                      "options.get_options")

    return flask.jsonify(data)


@options_module.bp.route("/", strict_slashes=False, methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def create_option():
    """ Creates option

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
            Successfully created option. Returns link to get option.

            produces:
                Application/json.

            Example::
                {
                    "option": link to get option
                }
        400:
            bad request. Returns message "no data provided" or invalid fields

            produces:
                Application/json.
    """

    data = flask.request.get_json() or {}

    if not data or not isinstance(data, dict):
        return errors.bad_request("no data provided or bad structure")

    try:
        option_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    option = option_model.Option.first(name=data["name"])

    if option is not None:
        return errors.bad_request(f"option '{data['name']}' already exists")

    option = option_model.Option(name=data["name"])

    app.db.session.add(option)
    app.db.session.commit()

    return flask.jsonify({
        "option":
        flask.url_for("options.get_option", id=option.id)
    }), 201


@options_module.bp.route("/<int:id>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_option(id):
    """Gets option.

    Retrieves single option from database.

    GET:
        Params:
            name (string) (required): option name.

    Responses:
        200:
            Successfully retrieves option. Returns option.

            produces:
                Application/json.

        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    option = option_model.Option.query.get_or_404(id)

    return flask.jsonify(option.to_dict())


@options_module.bp.route("/<int:id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def delete_option(id):
    """Deletes option.

    Deletes option from database.

    DELETE:
        Params:
            name (string) (required): name of option.

    Responses:
        200:
            Option successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            Option not found, returns message.

            produces:
                Application/json.
    """
    option = option_model.Option.query.get_or_404(id)

    app.db.session.delete(option)
    app.db.session.commit()

    return flask.jsonify({"message": "option deleted"})


@options_module.bp.route("/<int:id>/questions")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_questions(id):
    """Retrieves questions that has this option.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults
            to one.
            per_page (int) (optional): Number of items to retrieve per page,
            defaults to configuration constant PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".

    Responses:
        200:
            Paginated list of questions.

            Produces:
                Application/json.
        404:
            Option not found, returns message.

            produces:
                Application/json.
    """
    option = option_model.Option.query.get_or_404(id)

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    return flask.jsonify(
        option_model.Option.to_collection_dict(
            option.questions, page, per_page, "options.get_questions", id=id))
