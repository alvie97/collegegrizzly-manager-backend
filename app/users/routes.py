# create CRUD of users and protect the routes for admin only
# admins can't change other administrators
#TODO: add user schema validation

from . import bp
from app.security.utils import user_role, ADMINISTRATOR
from flask import request, jsonify
from common.utils import get_entity
from app.models.user import User


@bp.route("/", methods=["POST"])
@user_role([ADMINISTRATOR])
def create_user():

    data = request.get_json() or {}

    if not data:
        return jsonify({"message": "no data provided"}), 400

    user = User(**data)

    db.session.add(user)
    db.session.commit()


@bp.route("/<string:user_id>")
@user_role([ADMINISTRATOR])
@get_entity(User, "user")
def get_user(user):
    return jsonify({"user": user.to_dict()})


@bp.route("/<string:id>", methods=["PATCH"])
@user_role([ADMINISTRATOR])
@get_entity(User, "user")
def edit_user(user):
    data = request.get_json() or {}

    if not data:
        return jsonify({"message": "no data provided"}), 400

    user.update(data)
    db.session.commit()
    return jsonify("user saved successfully")


@bp.route("/<string:id>", methods=["DELETE"])
@user_role([ADMINISTRATOR])
@get_entity(User, "user")
def delete_user(user):
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "user deleted"})