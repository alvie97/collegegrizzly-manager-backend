import flask
import app
import marshmallow

from app import utils
from app.api import majors as majors_module
from app.models import major as major_model
from app.api import errors
from app.schemas import major_schema as major_schema_class
from app import security

major_schema = major_schema_class.MajorSchema()


@majors_module.bp.route("/", strict_slashes=False)
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_majors():
    """Gets majors in database

    Retrieves paginated list of all majors from database or majors that 
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
            of majors. See PaginatedAPIMixin.

            produces:
                Application/json.
    """

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = major_model.Major.query.filter(
            major_model.Major.name.like(f"%{search}%"))

        data = major_model.Major.to_collection_dict(
            query, page, per_page, "majors.get_majors", search=search)
    else:
        query = major_model.Major.query
        data = major_model.Major.to_collection_dict(query, page, per_page,
                                                    "majors.get_majors")

    return flask.jsonify(data)


@majors_module.bp.route("/", strict_slashes=False, methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def create_major():
    """ Creates major

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
            Successfully created major. Returns link to get major.

            produces:
                Application/json.

            Example::
                {
                    "major": link to get major
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
        major_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    major = major_model.Major.first(name=data["name"])

    if major is not None:
        return errors.bad_request(f"major '{data['name']}' already exists")

    major = major_model.Major(**data)

    app.db.session.add(major)
    app.db.session.commit()

    return flask.jsonify({
        "major":
        flask.url_for("majors.get_major", id=major.id)
    }), 201


@majors_module.bp.route("/<int:id>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_major(id):
    """Gets major.

    Retrieves single major from database.

    GET:
        Params:
            name (string) (required): major name.
    
    Responses:
        200:
            Successfully retieves major. Returns major.

            produces:
                Application/json.
        
        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    major = major_model.Major.query.get_or_404(id)

    return flask.jsonify(major.to_dict())


@majors_module.bp.route("/<int:id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def delete_major(id):
    """Deletes major.

    Deletes major from database.

    DELETE:
        Params:
            name (string) (required): name of major.
    
    Responses:
        200:
            Major successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            Major not found, returns message.

            produces:
                Application/json.
    """
    college = major_model.Major.query.get_or_404(id)

    app.db.session.delete(college)
    app.db.session.commit()

    return flask.jsonify({"message": "college deleted"})


@majors_module.bp.route("/<int:id>/colleges")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_colleges(id):
    """Retrieves colleges that has this major.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".

    Responses:
        200:
            Paginated list of colleges.

            Produces:
                Application/json.
        404:
            Major not found, returns message.

            produces:
                Application/json.
    """
    major = major_model.Major.query.get_or_404(id)

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    return flask.jsonify(
        major_model.Major.to_collection_dict(
            major.colleges, page, per_page, "majors.get_colleges", id=id))
