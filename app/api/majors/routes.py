import flask
import app

from app import utils
from app.api import majors as majors_module
from app.models import major as major_model


@majors_module.bp.route("/", strict_slashes=False)
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