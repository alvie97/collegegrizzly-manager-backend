# create CRUD of users and protect the routes for admin only
# admins can't change other administrators
#TODO: add user schema validation

from . import bp
from app import db
from app.security.utils import user_role, ADMINISTRATOR
from flask import request, jsonify, current_app
from app.common.utils import get_entity
from app.models.user import User
from app.security.utils import get_current_user
from sqlalchemy import not_, and_


@bp.route("/", methods=["POST"], strict_slashes=False)
@user_role([ADMINISTRATOR])
def create_user():

    data = request.get_json() or {}

    if not data:
        return jsonify({"message": "no data provided"}), 400

    user = User(**data)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "user added successfully"})


@bp.route("/", strict_slashes=False)
@user_role([ADMINISTRATOR])
def get_users():

    user_id = int(get_current_user())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get(
        "per_page", current_app.config["USERS_PER_PAGE"], type=int)

    search = request.args.get("search", "", type=str)

    if search:
        query = User.query.filter(
            and_(
                User.username.like("%{}%".format(search)),
                not_(User.id == user_id)))

        data = User.to_collection_dict(
            query, page, per_page, "users.get_users", search=search)
    else:
        query = User.query.filter(not_(User.id == user_id))
        data = User.to_collection_dict(query, page, per_page,
                                       "users.get_users")

    return jsonify(data)


@bp.route("/<string:username>")
@user_role([ADMINISTRATOR])
@get_entity(User, "username")
def get_user(user):
    return jsonify({"user": user.to_dict()})


@bp.route("/<string:username>", methods=["PATCH"])
@user_role([ADMINISTRATOR])
@get_entity(User, "username")
def edit_user(user: User):
    data = request.get_json() or {}

    if not data:
        return jsonify({"message": "no data provided"}), 400

    user.update(data)
    db.session.commit()
    return jsonify("user saved successfully")


@bp.route("/<string:username>", methods=["DELETE"])
@user_role([ADMINISTRATOR])
@get_entity(User, "username")
def delete_user(user):
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "user deleted"})