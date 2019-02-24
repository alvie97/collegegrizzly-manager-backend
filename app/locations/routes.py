import flask

from app.models import consolidated_city as consolidated_city_model
from app.models import county as county_model
from app.models import place as place_model
from app.models import state as state_model
from app import utils
from app import security

from app import locations


@locations.bp.route("/states")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_states():
    """Gets states in database

    Retrieves paginated list of all states from database or states that 
    contains the search request parameter if defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of states.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of states],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
    """
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)
    page = flask.request.args.get("page", 1, type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = state_model.State.query.filter(
            state_model.State.name.like("%{}%".format(search)))
        data = state_model.State.to_collection_dict(
            query, page, per_page, "locations.get_states", search=search)
    else:
        query = state_model.State.query
        data = state_model.State.to_collection_dict(query, page, per_page,
                                                    "locations.get_states")

    return flask.jsonify(data)


@locations.bp.route("/states/<string:fips_code>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(state_model.State, "fips_code")
def get_state(state):
    """Gets state.

    Retrieves single state from database.

    GET:
        Params:
            public_id (string) (required): public id of state.
    
    Responses:
        200:
            Successfully retieves state. Returns state.

            produces:
                Application/json.
        
        404:
            State not found, returns message.

            produces:
                Application/json.
    """
    return flask.jsonify(state.to_dict())


@locations.bp.route("/states/<string:state_fips>/counties")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(state_model.State, "fips_code")
def get_state_counties(state):
    """Gets state's counties in database

    Retrieves paginated list of all state's counties from database or 
    state's counties that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of states.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of counties],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            State not found, returns message.

            produces:
                Application/json.
    """
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)
    page = flask.request.args.get("page", 1, type=int)

    counties = state.counties

    return flask.jsonify(
        county_model.County.to_collection_dict(
            counties,
            page,
            per_page,
            "locations.get_state_counties",
            state_fips=state.fips_code))


@locations.bp.route("/states/<string:state_fips>/places")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(state_model.State, "fips_code")
def get_state_places(state):
    """Gets state's places in database

    Retrieves paginated list of all state's places from database or 
    state's places that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of states.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of places],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            State not found, returns message.

            produces:
                Application/json.
    """
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)
    page = flask.request.args.get("page", 1, type=int)

    places = state.places
    return flask.jsonify(
        place_model.Place.to_collection_dict(
            places,
            page,
            per_page,
            "locations.get_state_places",
            state_fips=state.fips_code))


@locations.bp.route("/states/<string:state_fips>/consolidated_cities")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(state_model.State, "fips_code")
def get_state_consolidated_cities(state):
    """Gets state's consolidated cities in database

    Retrieves paginated list of all state's consolidated cities from database or 
    state's consolidated cities that contains the search request parameter if 
    defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of states.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of consolidated cities],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
        404:
            State not found, returns message.

            produces:
                Application/json.
    """
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)
    page = flask.request.args.get("page", 1, type=int)

    consolidated_cities = state.consolidated_cities

    return flask.jsonify(
        consolidated_city_model.ConsolidatedCity.to_collection_dict(
            consolidated_cities,
            page,
            per_page,
            "locations.get_state_consolidated_cities",
            state_fips=state.fips_code))


@locations.bp.route("/counties")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_counties():
    """Gets counties in database

    Retrieves paginated list of all counties from database or counties that 
    contains the search request parameter if defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of counties.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of counties],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
    """
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)
    page = flask.request.args.get("page", 1, type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = county_model.County.query.filter(
            county_model.County.name.like("%{}%".format(search)))
        data = county_model.County.to_collection_dict(
            query, page, per_page, "locations.get_counties", search=search)
    else:
        query = county_model.County.query
        data = county_model.County.to_collection_dict(
            query, page, per_page, "locations.get_counties")

    return flask.jsonify(data)


@locations.bp.route("/places")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_places():
    """Gets places in database

    Retrieves paginated list of all places from database or places that 
    contains the search request parameter if defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of places.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of places],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
    """
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)
    page = flask.request.args.get("page", 1, type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = place_model.Place.query.filter(
            place_model.Place.name.like("%{}%".format(search)))
        data = place_model.Place.to_collection_dict(
            query, page, per_page, "locations.get_places", search=search)
    else:
        query = place_model.Place.query
        data = place_model.Place.to_collection_dict(query, page, per_page,
                                                    "locations.get_places")

    return flask.jsonify(data)


@locations.bp.route("/consolidated_cities")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_consolidated_cities():
    """Gets consolidated cities in database

    Retrieves paginated list of all consolidated cities from database or 
    consolidated cities that contains the search request parameter if defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant LOCATIONS_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of consolidated cities.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of consolidated cities],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page's url or None if there's no page,
                        "prev": previous page's url or None if there's no page,
                    }
                }
    """
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)
    page = flask.request.args.get("page", 1, type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = consolidated_city_model.ConsolidatedCity.query.filter(
            consolidated_city_model.ConsolidatedCity.name.like(
                "%{}%".format(search)))
        data = consolidated_city_model.ConsolidatedCity.to_collection_dict(
            query,
            page,
            per_page,
            "locations.get_consolidated_cities",
            search=search)
    else:
        query = consolidated_city_model.ConsolidatedCity.query
        data = consolidated_city_model.ConsolidatedCity.to_collection_dict(
            query, page, per_page, "locations.get_consolidated_cities")

    return flask.jsonify(data)
