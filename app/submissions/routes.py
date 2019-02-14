from flask import current_app, jsonify, request

from app import db
from app.models.college import College
from app.models.submission import Submission
from app.models.user import User
from app.security.utils import (ADMINISTRATOR, BASIC, MODERATOR,
                                get_current_user, user_role)
from app.common.utils import get_entity

from . import bp

from datetime import datetime


@bp.route("/submit", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
def submit():
    data = request.get_json() or {}

    if not data:
        return jsonify({"message": "no data provided"}), 400

    if "college_id" not in data:
        return jsonify({"message": "no college id provided"}), 400

    college = College.first(public_id=data["college_id"])

    if college is None:
        return jsonify({
            "message":
            f"college with id {data['college_id']} does not exist"
        })

    user_id = int(get_current_user())

    user = User.get(user_id)

    submission = Submission(
        college_name=college.name,
        submitted_by=user.username,
        college=college,
        user=user)

    db.session.add(submission)
    db.session.commit()

    return jsonify({"message": "submission successful"})


@bp.route("/", methods=["GET"], strict_slashes=False)
@user_role([ADMINISTRATOR, MODERATOR])
def get_submissions():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get(
        "per_page", current_app.config["SUBMISSIONS_PER_PAGE"], type=int)

    return jsonify({
        "submissions":
        Submission.to_collection_dict(Submission.query, page, per_page,
                                      "submissions.get_submissions")
    })


@bp.route("/assign_submission/<string:public_id>", methods=["POST"])
@user_role([ADMINISTRATOR, MODERATOR])
@get_entity(Submission, "public_id")
def assign_submission(submission: Submission):

    if submission.reviewed_by_admin is not None:
        return jsonify({
            "message":
            "submission already assigned to administrator"
        })

    user_id = int(get_current_user())
    user = User.get(user_id)

    if user.role == ADMINISTRATOR:
        submission.reviewed_by_admin = user.username
        db.session.commit()
        return jsonify({"message": "submission assigned successfully"})

    if submission.reviewed_by_moderator is None:
        submission.reviewed_by_moderator = user.username
        db.session.commit()
        return jsonify({"message": "submission assigned successfully"})


@bp.route("/<string:public_id>/approve", methods=["POST"])
@user_role([ADMINISTRATOR, MODERATOR])
@get_entity(Submission, "public_id")
def approve_submission(submission):

    if submission.status == "approved by administrator" or submission.status == "declined by administrator":
        return jsonify({
            "message":
            "submission already reviewed by an administrator"
        })

    user_id = int(get_current_user())
    user = User.get(user_id)

    if user.role == ADMINISTRATOR:
        submission.status = "approved by administrator"
        submission.reviewed_by_admin_at = datetime.utcnow()
        submission.reviewed_by_admin = user.username

    elif user.role == MODERATOR:

        if submission.status == "approved by moderator" or submission.status == "declined by moderator":
            return jsonify({
                "message":
                "submission already reviewed by a moderator, pending for administrator review"
            })

        submission.status = "approved by moderator"
        submission.reviewed_by_moderator_at = datetime.utcnow()
        submission.reviewed_by_moderator = user.username

    db.session.commit()

    return jsonify({"message": "approved submission"})