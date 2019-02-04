from flask import (flash, g, jsonify, get_flashed_messages, make_response,
                   redirect, render_template, request, url_for, current_app)
from sqlalchemy import or_

from . import bp
from app import db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from .utils import user_not_logged
from app.security.utils import get_current_user
from app.security.token_auth import (get_refresh_token_from_cookie,
                                     set_token_cookies, clear_token_cookies,
                                     revoke_user_tokens)
from app.security.csrf import clear_csrf_token_cookies


@bp.route("/login", methods=["POST", "GET"])
@user_not_logged
def login():
    if request.method == "GET":
        return render_template("login.html", messages=get_flashed_messages())

    id = request.form["id"]
    password = request.form["password"]

    if not id:
        flash("no username or email provided")
        return redirect(url_for("auth.login")), 422

    if not password:
        flash("no password provided")
        return redirect(url_for("auth.login")), 422

    user = User.query.filter(or_(User.username == id,
                                 User.email == id)).first()

    if user is None:
        flash(f"no user with username or email {id} found")
        return redirect(url_for("auth.login")), 404

    if not user.check_password(password):
        flash("invalid credentials")
        return redirect(url_for("auth.login")), 401

    response = make_response(redirect("/"))
    set_token_cookies(response, user.id, user.role)
    return response


@bp.route("/logout", methods=["POST"])
def logout():

    try:
        token = get_refresh_token_from_cookie()
        token = RefreshToken.first(token=token)

        if token is not None:
            user_id = token.user_id
        else:
            user_id = get_current_user()

    except KeyError:
        user_id = get_current_user()

    if user_id is not None:
        revoke_user_tokens(user_id)
        db.session.commit()

    response = make_response(jsonify({"message": "logout successful"}))
    clear_token_cookies(response)
    clear_csrf_token_cookies(response)

    return response
