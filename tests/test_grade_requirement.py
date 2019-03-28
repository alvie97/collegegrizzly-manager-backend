import flask
import app as application
import decimal
from app.models import scholarship as scholarship_model
from app.models import college as college_model
from app.models import grade_requirement_group
from app.models import association_tables
from app.models import grade as grade_model


def test_grade_requirement_scholarships_schema(app, scholarships, grades):
    """tests scholarships grade requirement"""

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        grade_count = grade_model.Grade.query.count()
        grades = grade_model.Grade.query.filter(
            grade_model.Grade.id.in_((1, 2, 3, 4))).all()
        grade_groups = [grades[:2], grades[2:]]

        for grade_group in grade_groups:
            group = scholarship.create_grade_requirement_group()

            for grade in grade_group:
                group.add_grade_requirement(grade, min=0.0)

        application.db.session.commit()

        scholarship = scholarship_model.Scholarship.query.first()

        ids = ((1, 2), (3, 4))

        for i, grade_group in enumerate(
                scholarship.grade_requirement_groups.all()):
            assert grade_group.grade_requirements.filter(
                association_tables.GradeRequirement.grade_id.in_(
                    ids[i])).distinct().count() == 2

        groups = scholarship.grade_requirement_groups.all()
        grade = grade_model.Grade.query.filter_by(id=ids[0][0]).first()
        groups[0].remove_grade_requirement(grade)
        scholarship.delete_grade_requirement_group(groups[1])

        application.db.session.commit()

        assert scholarship.grade_requirement_groups.count() == 1
        group = scholarship.grade_requirement_groups.first()
        assert group.grade_requirements.filter(
            association_tables.GradeRequirement.id.in_(ids[0])).count() == 1
        grade_requirement = group.grade_requirements.filter(
            association_tables.GradeRequirement.id.in_(ids[0])).first()
        assert grade_requirement.id == ids[0][1]

        assert grade_requirement_group.GradeRequirementGroup.query.count() == 1
        assert association_tables.GradeRequirement.query.count() == 1
        assert grade_model.Grade.query.count() == grade_count


def test_grade_requirement_colleges_schema(app, colleges, grades):
    """tests colleges grade requirement"""

    with app.app_context():
        college = college_model.College.query.first()
        grade_count = grade_model.Grade.query.count()
        grades = grade_model.Grade.query.filter(
            grade_model.Grade.id.in_((1, 2, 3, 4))).all()
        grade_groups = [grades[:2], grades[2:]]

        for grade_group in grade_groups:
            group = college.create_grade_requirement_group()

            for grade in grade_group:
                group.add_grade_requirement(grade, min=0.0)

        application.db.session.commit()

        college = college_model.College.query.first()

        ids = ((1, 2), (3, 4))

        for i, grade_group in enumerate(
                college.grade_requirement_groups.all()):
            assert grade_group.grade_requirements.filter(
                association_tables.GradeRequirement.grade_id.in_(
                    ids[i])).distinct().count() == 2

        groups = college.grade_requirement_groups.all()
        grade = grade_model.Grade.query.filter_by(id=ids[0][0]).first()
        groups[0].remove_grade_requirement(grade)
        college.delete_grade_requirement_group(groups[1])

        application.db.session.commit()

        assert college.grade_requirement_groups.count() == 1
        group = college.grade_requirement_groups.first()
        assert group.grade_requirements.filter(
            association_tables.GradeRequirement.id.in_(ids[0])).count() == 1
        grade_requirement = group.grade_requirements.filter(
            association_tables.GradeRequirement.id.in_(ids[0])).first()
        assert grade_requirement.id == ids[0][1]

        assert grade_requirement_group.GradeRequirementGroup.query.count() == 1
        assert association_tables.GradeRequirement.query.count() == 1
        assert grade_model.Grade.query.count() == grade_count


def test_get_grade_requirement_groups_scholarships(app, client, auth,
                                                   scholarships):
    """test get_grade_requirement_groups route for scholarships."""

    auth.login()

    with app.test_request_context():
        scholarship = scholarship_model.Scholarship.query.first()

        for i in range(10):
            scholarship.create_grade_requirement_group()

        application.db.session.commit()

        response = client.get(
            f"/api/scholarships/{scholarship.id}/grade_requirement_groups")

        assert response.status_code == 200
        assert response.get_json() == [
            group.to_dict()
            for group in scholarship.grade_requirement_groups.all()
        ]


def test_get_grade_requirement_groups_colleges(app, client, auth, colleges):
    """test get_grade_requirement_groups route for colleges."""

    auth.login()

    with app.test_request_context():
        college = college_model.College.query.first()

        for i in range(10):
            college.create_grade_requirement_group()

        application.db.session.commit()

        response = client.get(
            f"/api/colleges/{college.id}/grade_requirement_groups")

        assert response.status_code == 200
        assert response.get_json() == [
            group.to_dict()
            for group in college.grade_requirement_groups.all()
        ]


def test_post_grade_requirement_groups_scholarship_failure(
        app, client, auth, scholarships):
    """tests adding grade requirement group to scholarship, failure cases"""

    auth.login()

    response = client.post("/api/scholarships/99999/grade_requirement_groups")
    assert response.status_code == 404


def test_post_grade_requirement_groups_college_failure(app, client, auth,
                                                       colleges):
    """tests adding grade requirement group to college, failure cases"""

    auth.login()

    response = client.post("/api/colleges/99999/grade_requirement_groups")
    assert response.status_code == 404


def test_post_grade_requirement_groups_scholarship_success(
        app, client, auth, scholarships):
    """tests adding grade requirement group to scholarship, success cases"""

    auth.login()

    response = client.post("/api/scholarships/1/grade_requirement_groups")
    assert response.status_code == 201

    response = client.post("/api/scholarships/1/grade_requirement_groups")
    assert response.status_code == 201

    with app.test_request_context():
        scholarship = scholarship_model.Scholarship.query.first()
        assert scholarship.grade_requirement_groups.count() == 2
        group = scholarship.grade_requirement_groups.filter_by(id=2).first()
        assert group.to_dict() == response.get_json()


def test_delete_grade_requirement_groups_scholarship_failure(
        app, client, auth, scholarships):
    """tests removing grade requirement group to scholarship, failure cases"""

    auth.login()

    response = client.delete(
        "/api/scholarships/9999/grade_requirement_groups/1")
    assert response.status_code == 404

    response = client.delete("/api/scholarships/1/grade_requirement_groups/1")
    assert response.status_code == 404
    assert response.get_json(
    )["message"] == "scholarship doesn't have grade " \
                    "requirement group with id 1"


def test_delete_grade_requirement_groups_scholarship_success(
        app, client, auth, scholarships):
    """tests removing grade requirement group to scholarship, success cases"""

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        scholarship.create_grade_requirement_group()
        scholarship.create_grade_requirement_group()

        application.db.session.commit()

    auth.login()

    response = client.delete("/api/scholarships/1/grade_requirement_groups/1")
    assert response.status_code == 200

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()

        assert scholarship.grade_requirement_groups.count() == 1
        assert scholarship.grade_requirement_groups.filter_by(
            id=2).count() == 1


def test_post_grade_requirement_groups_college_success(app, client, auth,
                                                       colleges):
    """tests adding grade requirement group to college"""

    auth.login()

    response = client.post("/api/colleges/1/grade_requirement_groups")
    assert response.status_code == 201

    response = client.post("/api/colleges/1/grade_requirement_groups")
    assert response.status_code == 201

    with app.test_request_context():
        college = college_model.College.query.first()
        assert college.grade_requirement_groups.count() == 2
        group = college.grade_requirement_groups.filter_by(id=2).first()
        assert group.to_dict() == response.get_json()


def test_delete_grade_requirement_groups_college_failure(
        app, client, auth, colleges):
    """tests removing grade requirement group to college, failure cases"""

    auth.login()

    response = client.delete(
        "/api/colleges/9999/grade_requirement_groups/1")
    assert response.status_code == 404

    response = client.delete("/api/colleges/1/grade_requirement_groups/1")
    assert response.status_code == 404
    assert response.get_json(
    )["message"] == "college doesn't have grade " \
                    "requirement group with id 1"

def test_delete_grade_requirement_groups_college_success(
        app, client, auth, colleges):
    """tests removing grade requirement group to college"""

    with app.app_context():
        college = college_model.College.query.first()
        college.create_grade_requirement_group()
        college.create_grade_requirement_group()

        application.db.session.commit()

    auth.login()

    response = client.delete("/api/colleges/1/grade_requirement_groups/1")
    assert response.status_code == 200

    with app.app_context():
        college = college_model.College.query.first()

        assert college.grade_requirement_groups.count() == 1
        assert college.grade_requirement_groups.filter_by(id=2).count() == 1


def test_add_grade_requirement_to_grade_requirement_group_success(
        app, client, auth, grades):
    """tests adding grade requirement to grade requirement group"""

    auth.login()

    with app.app_context():
        group = grade_requirement_group.GradeRequirementGroup()
        application.db.session.add(group)
        application.db.session.commit()

    json = [{
        "grade_id": 1,
        "min": 2.4,
        "max": 4.0
    }, {
        "grade_id": 2,
        "min": None,
        "max": 4.0
    }]

    response = client.post(
        "/api/grade_requirement_groups/1/grade_requirements", json=json)

    assert response.status_code == 200

    with app.test_request_context():
        assert response.get_json() == {
            "grade_requirements":
            flask.url_for(
                "grade_requirement_groups.get_grade_requirements", id=1)
        }

    with app.app_context():
        group = grade_requirement_group.GradeRequirementGroup.query.first()

        assert group.grade_requirements.count() == 2
        assert group.grade_requirements.filter(
            association_tables.GradeRequirement.grade_id.in_(
                (json[0]["grade_id"],
                 json[1]["grade_id"]))).distinct().count() == 2

        requirement_0 = group.grade_requirements.filter_by(
            grade_id=json[0]["grade_id"]).first()
        requirement_1 = group.grade_requirements.filter_by(
            grade_id=json[1]["grade_id"]).first()

        assert requirement_0.min == decimal.Decimal(str(json[0]["min"]))
        assert requirement_0.max == decimal.Decimal(str(json[0]["max"]))

        assert requirement_1.min == requirement_1.grade.min


def test_remove_grade_requirement_from_grade_requirement_group_success(
        app, client, auth, grades):
    """tests removing grade requirement from grade requirement group"""

    auth.login()
    ids = (1, 2)
    with app.app_context():
        group = grade_requirement_group.GradeRequirementGroup()
        application.db.session.add(group)
        grades = grade_model.Grade.query.filter(
            grade_model.Grade.id.in_(ids)).all()

        for grade in grades:
            group.add_grade_requirement(grade)
        application.db.session.commit()

    response = client.delete(
        "/api/grade_requirement_groups/1/grade_requirements", json=[ids[1]])

    assert response.status_code == 200
    with app.test_request_context():
        assert response.get_json() == {
            "grade_requirements":
            flask.url_for(
                "grade_requirement_groups.get_grade_requirements", id=1)
        }

    with app.app_context():
        group = grade_requirement_group.GradeRequirementGroup.query.first()

        assert group.grade_requirements.count() == 1
        assert group.grade_requirements.filter_by(grade_id=ids[0]).count() == 1
