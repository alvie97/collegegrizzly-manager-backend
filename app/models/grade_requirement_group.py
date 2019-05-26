import app
from app.models.common import base_mixin, paginated_api_mixin
from app.models import association_tables
import flask


class GradeRequirementGroup(app.db.Model, base_mixin.BaseMixin,
                            paginated_api_mixin.PaginatedAPIMixin):
    """Grade requirement group.

    only one of the grades in this group is needed as requirement.

    Attributes:
         id (integer): model id.
         grade_requirements (sqlalchemy.relationship): grade requirements of
             group.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    scholarship_id = app.db.Column(app.db.Integer,
                                   app.db.ForeignKey("scholarship.id"))
    college_id = app.db.Column(app.db.Integer, app.db.ForeignKey("college.id"))
    grade_requirements = app.db.relationship(
        "GradeRequirement",
        cascade="all, delete-orphan",
        backref="grade_requirement_groups",
        lazy="dynamic")

    def __repr__(self):
        return f"<GradeRequirementGroup {self.id}>"

    def has_grade_requirement(self, grade_id):
        """checks if grade requirement group has grade requirement.

        Args:
            grade_id (int): grade id.
        Returns:
            bool: True if grade requirement group has grade requirement.
        """
        return self.grade_requirements.filter(
            association_tables.GradeRequirement.grade_id ==
            grade_id).count() > 0

    def add_grade_requirement(self, grade, min=None, max=None):
        """Adds grade requirement to grade requirement group.

        Args:
            grade (grade_model.Grade): grade model instance.
            min (float): min grade.
            max (float): max grade.
        """
        if min is not None and not (grade.min <= min <= grade.max):
            return

        if max is not None and not (grade.min <= max <= grade.max):
            return

        if min is not None and max is not None:
            if min > max:
                return

        if not self.has_grade_requirement(grade.id):
            grade_requirement = association_tables.GradeRequirement(
                min=min, max=max)
            app.db.session.add(grade_requirement)
            grade_requirement.grade = grade
            self.grade_requirements.append(grade_requirement)

    def remove_grade_requirement(self, grade):
        """Removes grade requirement to grade requirement group.

        Args:
            grade (grade_model.Grade): grade model instance.
        """
        if self.has_grade_requirement(grade.id):
            grade_requirement = self.grade_requirements.filter(
                association_tables.GradeRequirement.grade_id == grade.
                id).first()
            self.grade_requirements.remove(grade_requirement)

    def to_dict(self):
        return {
            "id": self.id,
            "links": {
                "get_grade_requirements":
                flask.url_for(
                    "grade_requirement_groups.get_grade_requirements",
                    id=self.id)
            }
        }
