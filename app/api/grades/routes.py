import flask
import app
import marshmallow

from app.api import grades as grades_module
from app.models import grade as grade_model
from app.api import errors
from app.schemas import grade_schema as grade_schema_class
from app import security

grade_schema = grade_schema_class.GradeSchema()


@grades_module.bp.route("/", strict_slashes=False)
def get_grades():
    """Gets grades in database

    Retrieves paginated list of all grades from database or grades that
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
            of grades. See PaginatedAPIMixin.

            produces:
                Application/json.
    """

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = grade_model.Grade.query.filter(
            grade_model.Grade.name.like(f"%{search}%"))

        data = grade_model.Grade.to_collection_dict(
            query, page, per_page, "grades.get_grades", search=search)
    else:
        query = grade_model.Grade.query
        data = grade_model.Grade.to_collection_dict(query, page, per_page,
                                                    "grades.get_grades")

    return flask.jsonify(data)


@grades_module.bp.route("/", strict_slashes=False, methods=["POST"])
def create_grade():
    """ Creates grade

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
            Successfully created grade. Returns link to get grade.

            produces:
                Application/json.

            Example::
                {
                    "grade": link to get grade
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
        grade_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    if data["min"] > data["max"]:
        return errors.bad_request("max value must be bigger or equal than min")

    grade = grade_model.Grade.first(name=data["name"])

    if grade is not None:
        return errors.bad_request(f"grade '{data['name']}' already exists")

    grade = grade_model.Grade(**data)

    app.db.session.add(grade)
    app.db.session.commit()

    return flask.jsonify({
        "grade":
        flask.url_for("grades.get_grade", id=grade.id)
    }), 201


@grades_module.bp.route("/<int:id>")
def get_grade(id):
    """Gets grade.

    Retrieves single grade from database.

    GET:
        Params:
            name (string) (required): grade name.

    Responses:
        200:
            Successfully retieves grade. Returns grade.

            produces:
                Application/json.

        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    grade = grade_model.Grade.query.get_or_404(id)

    return flask.jsonify(grade.to_dict())


@grades_module.bp.route("/<int:id>", methods=["PATCH"])
def patch_grade(id):
    """Edits grade.
    PATCH:
        Params:
            name (string) (required): name of grade.
        Consumes:
            Application/json.
        Request Body:
            Dictionary of grade fields.
        Example::
            {
                "name": "example grade name"
            }
    Responses:
        200:
            Grade successfully modified. Returns message.
            Produces:
                Application/json.
        400:
            Empty json object. Returns message "no data provided".
            produces:
                Application/json.
        404:
            Grade not found, returns message.
            produces:
                Application/json.
        400:
            some or all of the fields are invalid. Returns error of
            invalid fields.
            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if data["min"] > data["max"]:
        return errors.bad_request("max value must be bigger or equal than min")

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        grade_schema.load(data, partial=True)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    grade = grade_model.Grade.query.get_or_404(id)

    grade.update(data)
    app.db.session.commit()
    return flask.jsonify({
        "grade":
        flask.url_for("grades.get_grade", id=grade.id)
    })


@grades_module.bp.route("/<int:id>", methods=["DELETE"])
def delete_grade(id):
    """Deletes grade.

    Deletes grade from database.

    DELETE:
        Params:
            name (string) (required): name of grade.

    Responses:
        200:
            Grade successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            Grade not found, returns message.

            produces:
                Application/json.
    """
    grade = grade_model.Grade.query.get_or_404(id)

    app.db.session.delete(grade)
    app.db.session.commit()

    return flask.jsonify({"message": "grade deleted"})
