from flask import (flash, g, jsonify, get_flashed_messages, make_response,
                   redirect, render_template, request, url_for, current_app)
from sqlalchemy import or_

from . import bp
from app import db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.token_schema import (access_token_required, set_token_cookies,
                              get_current_user, get_refresh_token_from_cookie)
from .utils import user_not_logged

from .csrf import csrf_token_required


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
    set_token_cookies(response, user.username)
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
        RefreshToken.revoke_user_tokens(user_id)
        db.session.commit()

    response = make_response(jsonify({"message": "logout successful"}))

    access_cookie_name = current_app.config["ACCESS_COOKIE_NAME"]
    refresh_cookie_name = current_app.config["REFRESH_COOKIE_NAME"]
    csrf_cookie_name = current_app.config["CSRF_COOKIE_NAME"]
    secure_token_cookies = current_app.config["SECURE_TOKEN_COOKIES"]

    response.set_cookie(
        access_cookie_name,
        "",
        expires=0,
        secure=secure_token_cookies,
        httponly=True)
    response.set_cookie(
        refresh_cookie_name,
        "",
        expires=0,
        secure=secure_token_cookies,
        httponly=True)
    response.set_cookie(
        csrf_cookie_name,
        "",
        expires=0,
        secure=secure_token_cookies,
        httponly=True)

    return response
