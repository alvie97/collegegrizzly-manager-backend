# create CRUD of users and protect the routes for admin only
# admins can't change other administrators
#TODO: add user schema validation
#TODO: document routes

from flask import current_app, jsonify, request
from sqlalchemy import and_, not_

from app import db
from app.models.user import User
from app.security.utils import ADMINISTRATOR, get_current_user

from . import bp


@bp.route("/", methods=["POST"], strict_slashes=False)
def create_user():

    data = request.get_json() or {}

    if not data:
        return jsonify({"message": "no data provided"}), 400

    user = User(**data)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "user added successfully"})


@bp.route("/", strict_slashes=False)
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
def get_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return jsonify({"user": user.to_dict()})


@bp.route("/<string:username>", methods=["PATCH"])
def edit_user(username):
    data = request.get_json() or {}

    if not data:
        return jsonify({"message": "no data provided"}), 400

    user = User.query.filter_by(username=username).first_or_404()

    user.update(data)
    db.session.commit()
    return jsonify("user saved successfully")


@bp.route("/<string:username>", methods=["DELETE"])
def delete_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "user deleted"})
