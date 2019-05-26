import flask
import app

from app.models.common import base_mixin
from app.models.common import date_audit
from app.models.common import paginated_api_mixin
from app.models import scholarship_details as scholarship_details_model
from app.models import association_tables
from app.models import question as question_model
from app.models import grade_requirement_group


class Scholarship(app.db.Model, paginated_api_mixin.PaginatedAPIMixin,
                  date_audit.DateAudit, base_mixin.BaseMixin):
    """Scholarship model

    Attributes:
        id (integer): model id.
        scholarship_details (SQLAlchemy.relationship): scholarship details.
        additional_details (SQLAlchemy.relationship): additional scholarship
            details.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    exclude_from_match = app.db.Column(app.db.Boolean, default=False)
    college_id = app.db.Column(app.db.Integer, app.db.ForeignKey("college.id"))
    scholarship_details = app.db.relationship(
        "ScholarshipDetails",
        uselist=False,
        backref="scholarship",
        cascade="all, delete-orphan")

    additional_details = app.db.relationship(
        "Detail",
        backref="scholarship",
        cascade="all, delete-orphan",
        lazy="dynamic")

    scholarships_needed = app.db.relationship(
        "Scholarship",
        secondary=association_tables.scholarships_needed,
        primaryjoin=(association_tables.scholarships_needed.c.needs_id == id),
        secondaryjoin=(
            association_tables.scholarships_needed.c.needed_id == id),
        backref=app.db.backref("needed_by_scholarships", lazy="dynamic"),
        lazy="dynamic")
    programs_requirement = app.db.relationship(
        "ProgramRequirement", lazy="dynamic")

    chosen_college_requirement = app.db.relationship(
        "Question",
        secondary=association_tables.chosen_college_requirement,
        backref=app.db.backref("scholarship", lazy="dynamic"),
        lazy="dynamic")
    boolean_requirement = app.db.relationship(
        "BooleanRequirement", lazy="dynamic")

    grade_requirement_groups = app.db.relationship(
        "GradeRequirementGroup",
        backref="scholarships",
        cascade="all, delete-orphan",
        lazy="dynamic")

    location_requirements = app.db.relationship(
        "Location",
        backref="scholarship",
        cascade="all, delete-orphan",
        lazy="dynamic")
    selection_requirements = app.db.relationship(
        "SelectionRequirement", lazy="dynamic")

    str_repr = "scholarship"

    def __repr__(self):
        return f"<Scholarship {self.id}>"

    def get_additional_details(self):
        """Retrieves additional scholarship details.

        Args:
            self (class): scholarship class.
        Returns:
            list: additional scholarship details.
        """
        return [detail.to_dict() for detail in self.additional_details.all()]

    def has_detail(self, detail_name):
        """checks if scholarship has additional detail.

        Args:
            self (class): scholarship class.
            detail_name (string): detail name.
        Returns:
            Boolean: true if scholarship has major, false otherwise.

        """
        details = scholarship_details_model.ScholarshipDetails.ATTR_FIELDS
        additional_details_count = self.additional_details.filter_by(
            name=detail_name).count()

        return detail_name not in details and additional_details_count > 0

    def add_additional_detail(self, detail):
        """Adds additional detail to scholarship.

        Args:
            self (class): scholarship class.
            detail (sqlalchemy.Model): detail object.
        """
        if not self.has_detail(detail.name):
            self.additional_details.append(detail)

    def remove_additional_detail(self, detail):
        """Removes additional detail to scholarship.

        Args:
            self (class): scholarship class.
            detail (sqlalchemy.Model): detail object.
        """
        if self.has_detail(detail.name):
            self.additional_details.remove(detail)

    def add_needed_scholarship(self, scholarship):
        """ Adds scholarship needed.

        Args:
             self (class): scholarship class.
             scholarship (Scholarship): scholarship to add.
        """
        if not self.needs_scholarship(scholarship):
            self.scholarships_needed.append(scholarship)

    def remove_needed_scholarship(self, scholarship):
        """ Removes scholarship needed.

        Args:
             self (class): scholarship class.
             scholarship (Scholarship): scholarship to remove.
        """
        if self.needs_scholarship(scholarship):
            self.scholarships_needed.remove(scholarship)

    def needs_scholarship(self, scholarship_needed):
        """checks if scholarship needs scholarship needed.
        
        Args:
            self (class): scholarship class.
            scholarship_needed (Scholarship): scholarship to check.
        """
        return self.scholarships_needed.filter(
            association_tables.scholarships_needed.c.needed_id ==
            scholarship_needed.id).count() > 0

    def has_chosen_college_requirement(self, question):
        """
        Checks if scholarship has question as chosen college requirement.
        Args:
            question (object:Question): question to check.

        Returns:
            bool: true if question is in chosen_college_requirement, false
                otherwise.
        """

        return self.chosen_college_requirement.filter(
            association_tables.chosen_college_requirement.c.question_id ==
            question.id).count() > 0

    def add_chosen_college_requirement(self, question):
        """
        Adds question to scholarship's chosen college requirement.

        Args:
            question (obj:Question): question to add.
        """

        if not self.has_chosen_college_requirement(question):
            self.chosen_college_requirement.append(question)

    def remove_chosen_college_requirement(self, question):
        """
        Removes question to scholarship's chosen college requirement.

        Args:
            question (obj:Question): question to remove.
        """

        if self.has_chosen_college_requirement(question):
            self.chosen_college_requirement.remove(question)

    def has_boolean_requirement(self, question):
        """
        Checks if scholarship has question as boolean requirement.
        Args:
            question (object:Question): question to check.

        Returns:
            bool: true if question is in boolean_requirement, false
                otherwise.
        """

        return self.boolean_requirement.filter(
            association_tables.BooleanRequirement.question_id == question.
            id).count() > 0

    def add_boolean_requirement(self, question, required_value):
        """
        Adds question to scholarship's boolean requirement.

        Args:
            question (obj:Question): question to add.
            required_value (boolean): required boolean value.
        """

        if not self.has_boolean_requirement(question):
            boolean_requirement = association_tables.BooleanRequirement(
                required_value=required_value)
            boolean_requirement.question = question
            app.db.session.add(boolean_requirement)
            self.boolean_requirement.append(boolean_requirement)

    def remove_boolean_requirement(self, question):
        """
        Removes question to scholarship's boolean requirement.

        Args:
            question (obj:Question): question to remove.
        """

        if self.has_boolean_requirement(question):
            requirement = self.boolean_requirement.filter(
                question_model.Question.id == question.id).first()
            self.boolean_requirement.remove(requirement)

    def has_grade_requirement_group(self, group):
        """
        checks if scholarship has grade requirement group.

        Args:
            group (association_tables.GradeRequirementGroup): grade requirement
                group.

        Returns:
            bool: True if scholarship has grade requirement group.
        """
        return self.grade_requirement_groups.filter_by(id=group.id).count() > 0

    def create_grade_requirement_group(self):
        """creates and adds grade requirement group to scholarship.

        Returns:
            grade_requirement_group.GradeRequirementGroup: returns created
                group.
        """
        group = grade_requirement_group.GradeRequirementGroup()
        app.db.session.add(group)
        self.grade_requirement_groups.append(group)
        return group

    def delete_grade_requirement_group(self, group):
        """
        Removes grade requirement group from scholarship and deletes it.

        Args:
            group (association_tables.GradeRequirementGroup): grade requirement
                group.
        """
        if self.has_grade_requirement_group(group):
            self.grade_requirement_groups.remove(group)
            app.db.session.delete(group)

    def has_location_requirement(self, location):
        """
        Checks if location requirement exists.

        location: location to check.
        """

        return self.location_requirements.filter_by(id=location.id).count() > 0

    def add_location_requirement(self, location):
        """
        Adds location to location requirements.

        Args:
            location: location model instance to add.
        """

        if not self.has_location_requirement(location):
            self.location_requirements.append(location)

    def remove_location_requirement(self, location):
        """
        Removes location from location requirements.

        Args:
            location: location model instance to remove.
        """

        if self.has_location_requirement(location):
            self.location_requirements.remove(location)

    def has_selection_requirement(self, question_id):
        """
        Checks if scholarship has question as boolean requirement.
        Args:
            question (integer): question id to check.

        Returns:
            bool: true if question is in selection_requirement, false
                otherwise.
        """

        return self.selection_requirements.filter(
            association_tables.SelectionRequirement.question_id ==
            question_id).count() > 0

    def add_selection_requirement(self, question, description=None):
        """
        Adds selection requirement to scholarship.

        Args:
            question: question to add.
            description: question description. (optional)
        """

        if not self.has_selection_requirement(question.id):
            requirement = association_tables.SelectionRequirement(
                description=description)
            requirement.question = question
            app.db.session.add(requirement)
            self.selection_requirements.append(requirement)

    def remove_selection_requirement(self, selection_requirement):
        """
        Removes selection requirement from scholarship.

        Args:
            selection_requirement: selection requirement to remove.
        """

        if self.has_selection_requirement(selection_requirement.question.id):
            self.selection_requirements.remove(selection_requirement)

    def for_pagination(self):
        """ Serializes model for pagination.

        Returns:
            Dict: returns serialized object for pagination.
        """
        return {
            "id": self.id,
            "name": self.scholarship_details.name,
            "audit_dates": self.audit_dates(),
            "links": {
                "get_scholarship":
                flask.url_for("scholarships.get_scholarship", id=self.id)
            }
        }

    def to_dict(self):
        """ Serializes model.

        Returns:
            Dict: returns serialized object.
        """
        return {
            "id": self.id,
            "audit_dates": self.audit_dates(),
            "details": self.scholarship_details.to_dict(),
            "settings": {
                "exclude_from_match": self.exclude_from_match
            },
            "links": {
                "get_scholarships_needed":
                flask.url_for(
                    "scholarships.get_scholarships_needed", id=self.id)
            }
        }
