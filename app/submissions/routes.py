from datetime import datetime

from flask import current_app, jsonify, request

from app import db
from app.models.college import College
from app.models.submission import Submission
from app.models.user import User
from app.security.utils import (ADMINISTRATOR, BASIC, get_current_user,
                                user_role)
from app.utils import get_entity

from . import bp


@bp.route("/submit/<string:public_id>", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
@get_entity(College, "public_id")
def submit(college):

    pending_submissions = college.submissions.filter_by(
        status="pending").first()

    if pending_submissions is not None:
        return jsonify({
            "message":
            f"college '{college.name}' has pending submissions"
        }), 422

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
@user_role([ADMINISTRATOR])
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
@user_role([ADMINISTRATOR])
@get_entity(Submission, "public_id")
def assign_submission(submission):

    if submission.assigned_to is not None:
        return jsonify({"message": "submission already assigned"}), 422

    user_id = int(get_current_user())
    user = User.get(user_id)

    submission.assigned_to = user.username
    db.session.commit()

    return jsonify({"message": "submission assigned successfully"})


@bp.route("/<string:public_id>/approve", methods=["POST"])
@user_role([ADMINISTRATOR])
@get_entity(Submission, "public_id")
def approve_submission(submission):

    user_id = int(get_current_user())
    user = User.get(user_id)

    if user is None or user.username != submission.assigned_to:
        return jsonify({
            "message": "this submission was not assigned to you"
        }), 403

    if submission.status != "pending":
        return jsonify({
            "message":
            "submission already reviewed by an administrator"
        }), 422

    submission.status = "approved"
    submission.reviewed_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"message": "submission approved"})


@bp.route("/<string:public_id>/decline", methods=["POST"])
@user_role([ADMINISTRATOR])
@get_entity(Submission, "public_id")
def decline_submission(submission):

    user_id = int(get_current_user())
    user = User.get(user_id)

    if user is None or user.username != submission.assigned_to:
        return jsonify({
            "message": "this submission was not assigned to you"
        }), 403

    if submission.status != "pending":
        return jsonify({
            "message":
            "submission already reviewed by an administrator"
        }), 422

    data = request.get_json() or {}

    if "declination_message" not in data or not data["declination_message"]:
        return jsonify({
            "message": "A reason for declination must be stated"
        }), 422

    submission.status = "declined"
    submission.reviewed_at = datetime.utcnow()
    submission.observation = data["declination_message"]

    db.session.commit()

    return jsonify({"message": "submission declined"})
