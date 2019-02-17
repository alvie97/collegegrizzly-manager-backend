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


@bp.route("/submit/<string:college_id>", methods=["POST"])
@user_role([ADMINISTRATOR, BASIC])
def submit(college_id):
    college = College.first(public_id=college_id)

    if college is None:
        return jsonify({
            "message":
            f"college with id {college_id} does not exist"
        })

    pending_submissions = college.submissions.filter_by(
        status="pending:").first()

    if pending_submissions is not None:
        return jsonify({
            "message":
            f"college {college.name} has pending submissions"
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
def assign_submission(submission):

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

    college = submission.college

    last_submission = college.submissions.order_by(
        Submission.id.desc()).first()

    if last_submission.id != submission.id:
        return jsonify({"message": "only the last submission can be changed"})

    status, reviewer = submission.status.split(':')

    if status != "pending" and reviewer == ADMINISTRATOR:
        return jsonify({
            "message":
            "submission already reviewed by an administrator"
        })

    user_id = int(get_current_user())
    user = User.get(user_id)

    if user.role == ADMINISTRATOR:
        submission.status = f"approved:{ADMINISTRATOR}"
        submission.reviewed_by_admin_at = datetime.utcnow()
        submission.reviewed_by_admin = user.username

    elif user.role == MODERATOR:

        if status != "pending" and reviewer == MODERATOR:
            return jsonify({
                "message":
                "submission already reviewed by a moderator, "
                "pending for administrator review"
            })

        submission.status = f"approved:{MODERATOR}"
        submission.reviewed_by_moderator_at = datetime.utcnow()
        submission.reviewed_by_moderator = user.username

    db.session.commit()

    return jsonify({"message": "submission approved"})


@bp.route("/<string:public_id>/decline", methods=["POST"])
@user_role([ADMINISTRATOR, MODERATOR])
@get_entity(Submission, "public_id")
def decline_submission(submission):

    college = submission.college

    last_submission = college.submissions.order_by(
        Submission.id.desc()).first()

    if last_submission.id != submission.id:
        return jsonify({"message": "only the last submission can be changed"})

    status, reviewer = submission.status.split(':')

    if status != "pending" and reviewer == ADMINISTRATOR:
        return jsonify({
            "message":
            "submission already reviewed by an administrator"
        })

    user_id = int(get_current_user())
    user = User.get(user_id)

    if user.role == ADMINISTRATOR:
        submission.status = f"declined:{ADMINISTRATOR}"
        submission.reviewed_by_admin_at = datetime.utcnow()
        submission.reviewed_by_admin = user.username

    elif user.role == MODERATOR:

        if status != "pending" and reviewer == MODERATOR:
            return jsonify({
                "message":
                "submission already reviewed by a moderator, "
                "pending for administrator review"
            })

        submission.status = f"declined:{MODERATOR}"
        submission.reviewed_by_moderator_at = datetime.utcnow()
        submission.reviewed_by_moderator = user.username

    db.session.commit()

    return jsonify({"message": "submission declined"})