# TODO: change documentation to convention
import flask
import flask_jwt_extended
import sqlalchemy

import app
from app import auth
from app.models import token_blacklist
from app.models import user as user_model
from app.api import errors
from app import security


@auth.bp.route("/login", methods=["POST"])
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
    data = flask.request.get_json() or {}

    if not data or not isinstance(data, dict):
        return errors.bad_request("no data provided or bad structure")

    id = data.get("id")
    password = data.get("password")

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


@auth.bp.route("/token/refresh", methods=["POST"])
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

    claims = flask_jwt_extended.get_raw_jwt()
    token = token_blacklist.TokenBlacklist.query.filter_by(
        jti=claims["jti"]).first()

    security.revoke_token(token)
    app.db.session.commit()

    response = flask.jsonify({"logout": True})
    flask_jwt_extended.unset_jwt_cookies(response)
    return response


@auth.bp.route("/logout/all", methods=["POST"])
@flask_jwt_extended.jwt_refresh_token_required
def logout_all():
    username = flask_jwt_extended.get_jwt_identity()

    security.revoke_all_user_tokens(username)
    app.db.session.commit()

    response = flask.jsonify({"logout": True})
    flask_jwt_extended.unset_jwt_cookies(response)
    return response


@auth.bp.route("/is_user_logged/")
@flask_jwt_extended.jwt_required
def is_user_logged():
    return flask.jsonify({"logged": True})