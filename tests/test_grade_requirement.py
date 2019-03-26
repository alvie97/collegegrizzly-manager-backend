import app as application
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
