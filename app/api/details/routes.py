import flask
from app.api import details as details_module
from app.models import detail as detail_model


@details_module.bp.route("/", strict_slashes=False)
def get_details():
    """Gets details in database

    Retrieves paginated list of all details from database or details that 
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
            of details. See PaginatedAPIMixin.

            produces:
                Application/json.
    """

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = detail_model.Detail.query.filter(
            detail_model.Detail.name.like(f"%{search}%"))

        data = detail_model.Detail.to_collection_dict(
            query, page, per_page, "details.get_details", search=search)
    else:
        query = detail_model.Detail.query
        data = detail_model.Detail.to_collection_dict(query, page, per_page,
                                                      "details.get_details")

    return flask.jsonify(data)