import functools
import uuid
import flask
import app
from app import errors


def generate_public_id():
    """Generates public id
    
    Returns:
        string: uuid without dashes.
    """
    return str(uuid.uuid4()).replace('-', '')


#TODO: add param for url param name.
def get_entity(entity, search_key, uri_param_name="public_id"):
    """Adds entity as argument to wrapped function.

    Args:
        entity (sqlalchemy.Model): database model.
        search_key (string): database model property name.
        uri_param_name (string) (optional): route param unique name.

    Returns:
        Obj (Flask response): if entity not found, returns message and 404 code.
    """

    def get_entity_decorator(f):

        @functools.wraps(f)
        def f_wrapper(*args, **kwargs):
            search_arguments = {search_key: kwargs[uri_param_name]}
            entity_obj = entity.first(**search_arguments)

            if entity_obj is None:
                return flask.jsonify({
                    "message":
                    entity.__str_repr__ + " not found"
                }), 404

            kwargs[entity.__str_repr__] = entity_obj
            del kwargs[uri_param_name]

            return f(*args, **kwargs)

        return f_wrapper

    return get_entity_decorator


def get_location_requirement(location, package_name, base_endpoint, entity,
                             **endpoint_args):
    """Gets location requirement.

    Args:
        location (Obj): location database model.
        package_name (string): name of the package.
        base_endpoint (string): uri base.
        entity (obj): entity database model.
        **endpoint_args: arguments for url_for.

    Returns:
        Obj (Flask response): paginated list of the location requirement.
    """
    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["LOCATIONS_PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    try:
        if search:
            locations = entity.search_location_requirement(
                search, location, package_name, base_endpoint, page, per_page,
                **endpoint_args)
        else:
            locations = entity.get_location_requirement(
                location, package_name, base_endpoint, page, per_page,
                **endpoint_args)

    except errors.LocationEntityError as err:
        print("errors.LocationEntityError:", err)
        return flask.jsonify({"message": "Error ocurred"}), 500

    return flask.jsonify(locations)


def post_location_requirement(location, entity):
    """Adds location requirement

    Args:
        location (obj): location database model.
        entity (obj): entity database model.
    Returns:
        Obj (Flask response): returns message, 200 if successfull, 400 if no 
            data provided and 500 if error.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "No data provided"}), 400

    for location_fips in data:
        location_to_add = location.query.filter_by(
            fips_code=location_fips).first()

        if location_to_add is not None:
            try:
                entity.add_location(location_to_add)
            except errors.LocationEntityError as err:
                print("errors.LocationEntityError:", err)
                return flask.jsonify({"message": "Error ocurred"}), 500

    app.db.session.commit()
    return flask.jsonify({"message": "Locations added"})


def delete_location_requirement(location, entity):
    """Deletes location requirement.

    Args:
        location (obj): location database model.
        entity (obj): entity database model.
    Returns: 
        Obj (Flask response): returns message, 200 if success, 400 if no data
            provided and 500 if error.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "No data provided"}), 400

    for location_fips in data:
        location_to_delete = location.query.filter_by(
            fips_code=location_fips).first()

        if location is not None:
            try:
                entity.remove_location(location_to_delete)
            except errors.LocationEntityError as err:
                print("errors.LocationEntityError:", err)
                return flask.jsonify({"message": "Error ocurred"}), 500

    app.db.session.commit()
    return flask.jsonify({"message": "Locations removed"})


def get_locations_blacklist(location, package_name, base_endpoint, entity,
                            **endpoint_args):
    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    try:
        if search:
            locations = entity.search_locations_blacklist(
                search, location, package_name, base_endpoint, page, per_page,
                **endpoint_args)
        else:
            locations = entity.get_locations_blacklist(
                location, package_name, base_endpoint, page, per_page,
                **endpoint_args)

    except errors.LocationEntityError as err:
        print("errors.LocationEntityError:", err)
        return flask.jsonify({"message": "Error ocurred"}), 500

    return flask.jsonify(locations)


def post_locations_blacklist(location, entity):
    data = flask.request.get_json() or {}

    if not data or "location_fips" not in data:
        return flask.jsonify({"message": "No data provided"}), 400

    for location_fips in data["location_fips"]:
        location_to_add = location.query.filter_by(
            fips_code=location_fips).first()

        if location_to_add is not None:
            try:
                entity.add_location_to_blacklist(location_to_add)
            except errors.LocationEntityError as err:
                print("errors.LocationEntityError:", err)
                return flask.jsonify({"message": "Error ocurred"}), 500

    app.db.session.commit()
    return flask.jsonify({"message": "Locations added"})


def delete_locations_blacklist(location, entity):
    data = flask.request.get_json() or {}

    if not data or "location_fips" not in data:
        return flask.jsonify({"message": "No data provided"}), 400

    for location_fips in data["location_fips"]:
        location_to_delete = location.query.filter_by(
            fips_code=location_fips).first()

        if location is not None:
            try:
                entity.remove_location_from_blacklist(location_to_delete)
            except errors.LocationEntityError as err:
                print("errors.LocationEntityError:", err)
                return flask.jsonify({"message": "Error ocurred"}), 500

    app.db.session.commit()
    return flask.jsonify({"message": "Locations removed"})