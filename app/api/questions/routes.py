import flask
import app
import marshmallow

from app.api import questions as questions_module
from app.models import question as question_model
from app.models import option as option_model
from app.api import errors
from app.schemas import question_schema as question_schema_class
from app import security

question_schema = question_schema_class.QuestionSchema()


@questions_module.bp.route("/", strict_slashes=False)
def get_questions():
    """Gets questions in database

    Retrieves paginated list of all questions from database or questions that
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
            of questions. See PaginatedAPIMixin.

            produces:
                Application/json.
    """

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = question_model.Question.query.filter(
            question_model.Question.name.like(f"%{search}%"))

        data = question_model.Question.to_collection_dict(
            query, page, per_page, "questions.get_questions", search=search)
    else:
        query = question_model.Question.query
        data = question_model.Question.to_collection_dict(
            query, page, per_page, "questions.get_questions")

    return flask.jsonify(data)


@questions_module.bp.route("/", strict_slashes=False, methods=["POST"])
def create_question():
    """ Creates question

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
            Successfully created question. Returns link to get question.

            produces:
                Application/json.

            Example::
                {
                    "question": link to get question
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
        question_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    question = question_model.Question.first(name=data["name"])

    if question is not None:
        return errors.bad_request(f"question '{data['name']}' already exists")

    question = question_model.Question(**data)

    app.db.session.add(question)
    app.db.session.commit()

    return flask.jsonify({
        "question":
        flask.url_for("questions.get_question", id=question.id)
    }), 201


@questions_module.bp.route("/<int:id>")
def get_question(id):
    """Gets question.

    Retrieves single question from database.

    GET:
        Params:
            name (string) (required): question name.

    Responses:
        200:
            Successfully retieves question. Returns question.

            produces:
                Application/json.

        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    question = question_model.Question.query.get_or_404(id)

    return flask.jsonify(question.to_dict())


@questions_module.bp.route("/<int:id>", methods=["DELETE"])
def delete_question(id):
    """Deletes question.

    Deletes question from database.

    DELETE:
        Params:
            name (string) (required): name of question.

    Responses:
        200:
            Question successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            Question not found, returns message.

            produces:
                Application/json.
    """
    question = question_model.Question.query.get_or_404(id)

    app.db.session.delete(question)
    app.db.session.commit()

    return flask.jsonify({"message": "question deleted"})


@questions_module.bp.route("/<int:id>/options")
def get_options(id):
    """Gets question options in database

    Retrieves paginated list of all question options from database.

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
            of questions. See PaginatedAPIMixin.

            produces:
                Application/json.
    """
    question = question_model.Question.query.get_or_404(id)

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    return flask.jsonify(
        option_model.Option.to_collection_dict(
            question.options, page, per_page, "questions.get_options", id=id))


@questions_module.bp.route("/<int:id>/options", methods=["POST"])
def add_options(id):
    """Adds options to question

    POST:
        params:
            id (int): question id.

        Request body:
            list of options id.

            consumes:
                application/json.

    Returns:
        200:
            link to get question options.

            produces:
                application/json.
        404:
            no question found

            produces:
                application/json.
    """
    data = flask.request.get_json() or []

    if not data or not isinstance(data, list):
        return errors.bad_request("no data provided or bad structure")

    question = question_model.Question.query.get_or_404(id)

    for option_id in data:
        try:
            option_id = int(option_id)
        except ValueError:
            return errors.bad_request("option id must be an integer")

        option = option_model.Option.get(option_id)

        if option is not None:
            question.add_option(option)

    app.db.session.commit()

    return flask.jsonify({
        "options":
        flask.url_for("questions.get_options", id=id)
    })


@questions_module.bp.route("/<int:id>/options", methods=["DELETE"])
def delete_options(id):
    """removes options from question

    DELETE:
        params:
            id (int): question id.

        Request body:
            list of options id.

            consumes:
                application/json.

    Returns:
        200:
            link to get question options.

            produces:
                application/json.
        404:
            no question found

            produces:
                application/json.
    """
    data = flask.request.get_json() or []

    if not data or not isinstance(data, list):
        return errors.bad_request("no data provided or bad structure")

    question = question_model.Question.query.get_or_404(id)

    for option_id in data:

        try:
            option_id = int(option_id)
        except ValueError:
            return errors.bad_request("option id must be an integer")

        option = option_model.Option.get(option_id)

        if option is not None:
            question.remove_option(option)

    app.db.session.commit()

    return flask.jsonify({
        "options":
        flask.url_for("questions.get_options", id=id)
    })
