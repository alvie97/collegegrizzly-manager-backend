import flask
import flask_jwt_extended
import sqlalchemy

import app
from app import auth
from app.auth import utils as auth_utils
from app.models import token_blacklist
from app.models import user as user_model
from app.api import errors
from app import security


@auth.bp.route("/login", methods=["POST"])
@auth_utils.user_not_logged
def login():
    """ Loggs user to the application.

    Loggs user to the application, accepts POST and GET methods.

    Requires:
        Form data.

        id: user identification (username or email).
        password: user password

    Returns:
        redirects to application or loggin page if not successful
    """
    id = flask.request.form["id"]
    password = flask.request.form["password"]

    if not id:
        return errors.bad_request("no username or email provided")

    if not password:
        return errors.bad_request("no password provided")

    user = user_model.User.query.filter(
        sqlalchemy.or_(user_model.User.username == id,
                       user_model.User.email == id)).first()

    if user is None:
        return errors.not_found(f"no user with username or email {id} found")

    if not user.check_password(password):
        return errors.unauthorized("invalid credentials")

    response = flask.jsonify({"login": True})

    access_token = flask_jwt_extended.create_access_token(
        identity=user.username, user_claims={"role": user.role})

    refresh_token = flask_jwt_extended.create_refresh_token(
        identity=user.username, user_claims={"role": user.role})

    security.add_token_to_database(refresh_token)

    flask_jwt_extended.set_access_cookies(response, access_token)
    flask_jwt_extended.set_refresh_cookies(response, refresh_token)

    return response


@auth.bp.route("/token/refresh")
@flask_jwt_extended.jwt_refresh_token_required
def refresh_token():
    current_user = flask_jwt_extended.get_jwt_identity()
    claims = flask_jwt_extended.get_jwt_claims()
    access_token = flask_jwt_extended.create_access_token(
        identity=current_user, user_claims=claims)

    response = flask.jsonify({"refreshed": True})
    flask_jwt_extended.set_access_cookies(response, access_token)
    return response


@auth.bp.route("/logout", methods=["POST"])
@flask_jwt_extended.jwt_refresh_token_required
def logout():
    """Logs user out of the application.

    Logs user out of the application, accepts POST method.

    Returns:
        Json response.
    """
    username = flask_jwt_extended.get_current_user()
    user_count = user_model.User.query.filter_by(username=username).count()

    if user_count == 0:
        # if this occurs, the secret key got leaked
        return errors.not_found("user not found")

    token_claims = flask_jwt_extended.get_jwt_claims()
    token = token_blacklist.TokenBlacklist.query.filter_by(
        jti=token_claims["jti"], user=username).first()

    if token is None:
        # if this occurs, the secret key got leaked
        return errors.not_found("token not found")

    security.revoke_token(token)
    app.db.session.commit()

    response = flask.jsonify({"logout": True})
    flask_jwt_extended.unset_jwt_cookies(response)
    return response


@auth.bp.route("/logout/all", methods=["POST"])
@flask_jwt_extended.jwt_refresh_token_required
def logout_all():
    username = flask_jwt_extended.get_current_user()
    user_count = user_model.User.query.filter_by(username=username).count()

    if user_count == 0:
        # if this occurs, the secret key got leaked
        return errors.not_found("user not found")

    security.revoke_all_user_tokens(username)
    app.db.session.commit()

    response = flask.jsonify({"logout": True})
    flask_jwt_extended.unset_jwt_cookies(response)
    return response