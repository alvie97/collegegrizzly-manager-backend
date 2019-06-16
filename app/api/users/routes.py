import flask
import sqlalchemy
import marshmallow

import app
from app.models import user as user_model
from app.security import utils
from app.api import users as users_module
from app.api import errors
from app.schemas import user_schema as user_schema_class

user_schema = user_schema_class.UserSchema()


@users_module.bp.route("/", methods=["POST"], strict_slashes=False)
def create_user():
    """creates user.

    POST:
        Consumes:
            Application/json.
        Request body:
            dictionary with user data.
        
            Example::
                {
                    "username": "example_username",
                    "email": "example_email@example.com",
                    "password": "example_password"
                }
    Responses:
        201:
            Successfully created user. Returns link to get user.

            produces:
                Application/json.

            Example::
                {
                    "user": link to get user
                }
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        400:
            some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """

    data = flask.request.get_json() or {}

    if not data or not isinstance(data, dict):
        return errors.bad_request("no data provided or bad structure")

    try:
        user_schema.load(data)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    user = user_model.User(**data)

    app.db.session.add(user)
    app.db.session.commit()

    return flask.jsonify({
        "user":
        flask.url_for("users.get_user", username=data["username"])
    }), 201


@users_module.bp.route("/", strict_slashes=False)
def get_users():
    """Gets users in database

    Retrieves paginated list of all users from database or users that 
    contains the search flask.request parameter if defined.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant COLLEGE_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of users. See PaginatedAPIMixin.

            produces:
                Application/json.
    """
    user_id = int(utils.get_current_user())

    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    search = flask.request.args.get("search", "", type=str)

    if search:
        query = user_model.User.query.filter(
            sqlalchemy.and_(
                user_model.User.username.like("%{}%".format(search)),
                sqlalchemy.not_(user_model.User.id == user_id)))

        data = user_model.User.to_collection_dict(
            query, page, per_page, "users.get_users", search=search)
    else:
        query = user_model.User.query.filter(
            sqlalchemy.not_(user_model.User.id == user_id))
        data = user_model.User.to_collection_dict(query, page, per_page,
                                                  "users.get_users")

    return flask.jsonify(data)


@users_module.bp.route("/<string:username>")
def get_user(username):
    """Gets user.

    Retrieves single user from database.

    GET:
        Params:
            username (string) (required): username.
    
    Responses:
        200:
            Successfully retieves user. Returns user.

            produces:
                Application/json.
        
        404:
            User not found, returns message.

            produces:
                Application/json.
    """
    user = user_model.User.query.filter_by(username=username).first_or_404()
    return flask.jsonify({"user": user.to_dict()})


@users_module.bp.route("/<string:username>", methods=["PATCH"])
def edit_user(username):
    """Edits user.

    PATCH:
        Params:
            name (string) (required): name of user.

        Consumes:
            Application/json.
        
        Request Body:
            Dictionary of user editable fields.
        
        Example::
            {
                "username": "username example"
            }
    
    Responses:
        200:
            User successfully modified. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            User not found, returns message.

            produces:
                Application/json.
        400:
            some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    try:
        user_schema.load(data, partial=True)
    except marshmallow.ValidationError as err:
        return flask.jsonify(err.messages), 400

    user = user_model.User.query.filter_by(username=username).first_or_404()

    user.update(data)
    app.db.session.commit()
    return flask.jsonify({
        "user":
        flask.url_for("users.get_user", username=username)
    })


@users_module.bp.route("/<string:username>", methods=["DELETE"])
def delete_user(username):
    """Deletes user.

    Deletes user from database.

    DELETE:
        Params:
            name (string) (required): name of user.
    
    Responses:
        200:
            User successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            User not found, returns message.

            produces:
                Application/json.
    """
    user = user_model.User.query.filter_by(username=username).first_or_404()
    app.db.session.delete(user)
    app.db.session.commit()

    return flask.jsonify({"message": "user deleted"})
