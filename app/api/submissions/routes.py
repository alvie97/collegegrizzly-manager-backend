import datetime
import flask
import app
from app.models import college as college_model
from app.models import user as user_model
from app.models import submission as submission_model
from app import security
from app import utils
from app.api import submissions


@submissions.bp.route("/submit/<string:public_id>", methods=["POST"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(college_model.College, "public_id")
def submit(college):
    """Creates submission.

    POST:
    Responses:
        400:
            Returns message if college doesn't exist.

            Produces:
                Application/json.
        
        200:
            Returns message if success.
            Produces:
                Application/json.
    """

    pending_submissions = college.submissions.filter_by(
        status="pending").first()

    if pending_submissions is not None:
        return flask.jsonify({
            "message":
            f"college '{college.name}' has pending submissions"
        }), 400

    user_id = int(security.get_current_user())

    user = user_model.User.get(user_id)

    submission = submission_model.Submission(
        college_name=college.name,
        submitted_by=user.username,
        college=college,
        user=user)

    app.db.session.add(submission)
    app.db.session.commit()

    return flask.jsonify({"message": "submission successful"})


@submissions.bp.route("/", strict_slashes=False)
@security.user_role([security.ADMINISTRATOR])
def get_submissions():
    """Gets submissions in database

    Retrieves paginated list of all submissions from database.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant COLLEGE_PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of submissions. See PaginatedAPIMixin class.

            produces:
                Application/json. 
    """
    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["SUBMISSIONS_PER_PAGE"], type=int)

    return flask.jsonify({
        "submissions":
        submission_model.Submission.to_collection_dict(
            submission_model.Submission.query, page, per_page,
            "submissions.get_submissions")
    })


@submissions.bp.route(
    "/assign_submission/<string:public_id>", methods=["POST"])
@security.user_role([security.ADMINISTRATOR])
@utils.get_entity(submission_model.Submission, "public_id")
def assign_submission(submission):
    """Assigns submission to user.

    POST:
    Responses:
        404:
            Returns message if submission not found.
            Produces:
                Application/json.
        400:
            Returns message if submission is already assigned.
            Produces:
                Application/json.
        200:
            Returns success message.
            Produces:
                Application/json.
    """

    if submission.assigned_to is not None:
        return flask.jsonify({"message": "submission already assigned"}), 400

    user_id = int(security.get_current_user())
    user = user_model.User.get(user_id)

    submission.assigned_to = user.username
    app.db.session.commit()

    return flask.jsonify({"message": "submission assigned successfully"})


@submissions.bp.route("/<string:public_id>/approve", methods=["POST"])
@security.user_role([security.ADMINISTRATOR])
@utils.get_entity(submission_model.Submission, "public_id")
def approve_submission(submission):
    """Approves submission.

    POST:
    Responses:
        403:
            Returns message if submission was not assigned to the user.
            Produces:
                Application/json.
        404:
            Returns message if submission was not found.
            Produces:
                Application/json.
        400:
            Returns message if submission was already reviewed.
            Produces:
                Application/json.
        200:
            Returns success message.
            Produces:
                Application/json.
    """

    user_id = int(security.get_current_user())
    user = user_model.User.get(user_id)

    if user is None or user.username != submission.assigned_to:
        return flask.jsonify({
            "message":
            "this submission was not assigned to you"
        }), 403

    if submission.status != "pending":
        return flask.jsonify({
            "message":
            "submission already reviewed by an administrator"
        }), 400

    submission.status = "approved"
    submission.reviewed_at = datetime.datetime.utcnow()

    app.db.session.commit()

    return flask.jsonify({"message": "submission approved"})


@submissions.bp.route("/<string:public_id>/decline", methods=["POST"])
@security.user_role([security.ADMINISTRATOR])
@utils.get_entity(submission_model.Submission, "public_id")
def decline_submission(submission):
    """Declines submission.

    POST:
    Responses:
        403:
            Returns message if submission was not assigned to the user.
            Produces:
                Application/json.
        404:
            Returns message if submission was not found.
            Produces:
                Application/json.
        400:
            Returns message if submission was already reviewed.
            Produces:
                Application/json.
        200:
            Returns success message.
            Produces:
                Application/json.
    """
    user_id = int(security.get_current_user())
    user = user_model.User.get(user_id)

    if user is None or user.username != submission.assigned_to:
        return flask.jsonify({
            "message":
            "this submission was not assigned to you"
        }), 403

    if submission.status != "pending":
        return flask.jsonify({
            "message":
            "submission already reviewed by an administrator"
        }), 400

    data = flask.request.get_json() or {}

    if "declination_message" not in data or not data["declination_message"]:
        return flask.jsonify({
            "message":
            "A reason for declination must be stated"
        }), 400

    submission.status = "declined"
    submission.reviewed_at = datetime.datetime.utcnow()
    submission.observation = data["declination_message"]

    app.db.session.commit()

    return flask.jsonify({"message": "submission declined"})
