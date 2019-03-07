import flask
import sqlalchemy

import app
from app import auth
from app.auth import utils as auth_utils
from app.models import refresh_token
from app.models import user as user_model
from app.security import csrf, token_auth


@auth.bp.route("/login", methods=["POST", "GET"])
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
    if flask.request.method == "GET":
        return flask.render_template(
            "login.html", messages=flask.get_flashed_messages())

    id = flask.request.form["id"]
    password = flask.request.form["password"]

    if not id:
        flask.flash("no username or email provided")
        return flask.redirect(flask.url_for("auth.login")), 400

    if not password:
        flask.flash("no password provided")
        return flask.redirect(flask.url_for("auth.login")), 400

    user = user_model.User.query.filter(
        sqlalchemy.or_(user_model.User.username == id,
                       user_model.User.email == id)).first()

    if user is None:
        flask.flash(f"no user with username or email {id} found")
        return flask.redirect(flask.url_for("auth.login")), 404

    if not user.check_password(password):
        flask.flash("invalid credentials")
        return flask.redirect(flask.url_for("auth.login")), 401

    response = flask.make_response(flask.redirect("/"))
    token_auth.set_token_cookies(response, user.id, user.role)
    return response


@auth.bp.route("/logout", methods=["POST"])
def logout():
    """Logs user out of the application.

    Logs user out of the application, accepts POST method.

    Returns:
        Json response.
    """

    try:
        token = token_auth.get_refresh_token_from_cookie()
        token = refresh_token.RefreshToken.first(token=token)

        if token is not None:
            user_id = token.user_id
        else:
            user_id = security.get_current_user()

    except KeyError:
        user_id = security.get_current_user()

    if user_id is not None:
        token_auth.revoke_user_tokens(user_id)
        app.db.session.commit()

    response = flask.make_response(
        flask.jsonify({
            "message": "logout successful"
        }))
    token_auth.clear_token_cookies(response)
    csrf.clear_csrf_token_cookies(response)

    return response
