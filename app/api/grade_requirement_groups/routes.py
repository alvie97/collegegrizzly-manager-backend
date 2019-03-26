import flask

import app
from app.api import errors
from app.api import grade_requirement_groups as grade_requirement_groups_module
from app.models import grade as grade_model
from app.models import grade_requirement_group as grade_requirement_group_model


@grade_requirement_groups_module.bp.route("/<int:id>/grade_requirements")
def get_grade_requirements(id):
    """Gets group's grade requirements.

    GET:
        Args:
            id (integer): grade requirement group id.

    Responses:
        200:
            Returns list of grade requirements.

            Produces:
                Application/json.

        404:
            Grade requirement group not found.

            Produces:
                Application/json.
    """

    group = grade_requirement_group_model \
        .GradeRequirementGroup \
        .query \
        .get_or_404(id)

    return flask.jsonify([
        grade_requirement.to_dict()
        for grade_requirement in group.grade_requirements
    ])


@grade_requirement_groups_module.bp.route(
    "/<int:group_id>/grade_requirements/<int:grade_id>")
def get_grade_requirements(group_id, grade_id):
    """Gets grade requirement from group.

    GET:
        Args:
            group_id (integer): grade requirement group id.
            grade_id (integer): grade id.

    Responses:
        200:
            Returns grade requirement.

            Produces:
                Application/json.

        404:
            Grade requirement group or grade not found.

            Produces:
                Application/json.
    """

    group = grade_requirement_group_model \
        .GradeRequirementGroup \
        .query \
        .get_or_404(group_id)

    grade_requirement = group.grade_requirements.filter_by(
        grade_id=grade_id).first()

    if grade_requirement is None:
        return errors.bad_request("grade requirement group doesn't have "
                                  f"grade requirement for grade {grade_id}")

    return flask.jsonify(grade_requirement.to_dict())


@grade_requirement_groups_module.bp.route(
    "/<int:id>/grade_requirements", methods=["POST"])
def post_grade_requirement(id):
    """Adds grade requirement to group.

    POST:
        Args:
            id (integer): grade requirement group id.

        Consumes:
            Application/json.

        Request body:
            list of grade ids and, requirement's min and max.

            Example::
                [
                    {
                        "grade_id": grade id,
                        "min": min,
                        "max": max
                    }
                ]
    Responses:
        200:
            successfully adds grade requirements to grade requirement group.
            Returns url to get group's grade requirements.

            Produces:
                Application/json.

        400:
            no data provided or bad structure, invalid grade id, either
            range_min or range_max isn't a float, missing fileds.

            Produces:
                Application/json.

        404:
            either group or grade not found.

            Produces:
                Application/json.
    """
    data = flask.request.get_json() or []

    if not data and not isinstance(data, list):
        return errors.bad_request("no data provided or bad structure")

    group = grade_requirement_group_model \
        .GradeRequirementGroup \
        .query \
        .get_or_404(id)

    try:
        for grade_requirement in data:
            if not isinstance(grade_requirement, dict):
                return errors.bad_request("bad structure")

            try:
                grade_id = int(grade_requirement["grade_id"])
            except ValueError:
                return errors.bad_request("invalid grade id")

            try:
                range_min = float(
                    grade_requirement["min"]
                ) if grade_requirement["min"] is not None else None
                range_max = float(
                    grade_requirement["max"]
                ) if grade_requirement["max"] is not None else None
            except ValueError:
                return errors.bad_request("either range_min or range_max "
                                          "isn't a float")

            grade = grade_model.Grade.query.get_or_404(grade_id)
            group.add_grade_requirement(grade, range_min, range_max)

    except KeyError:
        return errors.bad_request("missing fields")

    app.db.session.commit()

    return flask.jsonify({
        "grade_requirements":
        flask.url_for(
            "grade_requirement_groups.get_grade_requirements", id=id)
    })


@grade_requirement_groups_module.bp.route(
    "/<int:id>/grade_requirements", methods=["DELETE"])
def delete_grade_requirement(id):
    """Removes grade requirement to group.

    DELETE:
        Args:
            id (integer): grade requirement group id.

        Consumes:
            Application/json.

        Request body:
            list of grade ids.

            Example::
                [ grade id, ...]
    Responses:
        200:
            successfully removes grade requirements to grade requirement group.
            Returns url to get group's grade requirements.

            Produces:
                Application/json.

        400:
            no data provided or bad structure, invalid grade id.

            Produces:
                Application/json.

        404:
            either group or grade not found.

            Produces:
                Application/json.
    """
    data = flask.request.get_json() or []

    if not data and not isinstance(data, list):
        return errors.bad_request("no data provided or bad structure")

    group = grade_requirement_group_model \
        .GradeRequirementGroup \
        .query \
        .get_or_404(id)

    for grade_id in data:

        try:
            grade_id = int(grade_id)
        except ValueError:
            return errors.bad_request("invalid grade id")

        grade = grade_model.Grade.query.get_or_404(grade_id)
        group.remove_grade_requirement(grade)

    app.db.session.commit()

    return flask.jsonify({
        "grade_requirements":
        flask.url_for(
            "grade_requirement_groups.get_grade_requirements", id=id)
    })
