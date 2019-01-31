# create CRUD of users and protect the routes for admin only
# admins can't change other administrators
from . import bp
from app.security.utils import user_role, ADMINISTRATOR


@bp.route("/", methods=["POST"])
@user_role([ADMINISTRATOR])
def create_user():
    pass


@bp.route("/<string:id>")
@user_role([ADMINISTRATOR])
def get_user():
    pass


@bp.route("/<string:id>", methods=["PATCH"])
@user_role([ADMINISTRATOR])
def edit_user():
    pass


@bp.route("/<string:id>", methods=["DELETE"])
@user_role([ADMINISTRATOR])
def delete_user():
    pass