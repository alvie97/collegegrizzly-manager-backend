import flask

import app
from app.models import option as option_model
from app.models.common import base_mixin, date_audit, paginated_api_mixin

college_major = app.db.Table(
    "college_major",
    app.db.Column("college_id", app.db.Integer,
                  app.db.ForeignKey("college.id")),
    app.db.Column("major_id", app.db.Integer, app.db.ForeignKey("major.id")))

program_qualification_round = app.db.Table(
    "program_qualification_round",
    app.db.Column("program_id", app.db.Integer,
                  app.db.ForeignKey("program.id")),
    app.db.Column("qualification_round_id", app.db.Integer,
                  app.db.ForeignKey("qualification_round.id")))

scholarships_needed = app.db.Table(
    "scholarships_needed",
    app.db.Column("needs_id", app.db.Integer,
                  app.db.ForeignKey("scholarship.id")),
    app.db.Column("needed_id", app.db.Integer,
                  app.db.ForeignKey("scholarship.id")))

program_requirement_qualification_round = app.db.Table(
    "program_requirement_qualification_round",
    app.db.Column("program_requirement_id", app.db.Integer,
                  app.db.ForeignKey("program_requirement.id")),
    app.db.Column("qualification_round_id", app.db.Integer,
                  app.db.ForeignKey("qualification_round.id")))

chosen_college_requirement = app.db.Table(
    "chosen_college_requirement",
    app.db.Column("scholarship_id", app.db.Integer,
                  app.db.ForeignKey("scholarship.id")),
    app.db.Column("question_id", app.db.Integer,
                  app.db.ForeignKey("question.id")))


class ProgramRequirement(app.db.Model, base_mixin.BaseMixin,
                         date_audit.DateAudit,
                         paginated_api_mixin.PaginatedAPIMixin):
    """ Program requirement.

    Holds relationship between program and scholarship. Scholarship needs
    program.

    Attributes:
        id (integer): Model id.
        scholarship_id (integer): scholarship id.
        program_id (integer): program id.
        program (sqlalchemy.Model): program.
        qualification_rounds (sqlalchemy.relationship): qualification rounds
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    scholarship_id = app.db.Column(
        "scholarship_id",
        app.db.Integer,
        app.db.ForeignKey("scholarship.id"),
        nullable=False)
    program_id = app.db.Column(
        "program_id",
        app.db.Integer,
        app.db.ForeignKey("program.id"),
        nullable=False)
    program = app.db.relationship("Program")
    qualification_rounds = app.db.relationship(
        "QualificationRound",
        secondary=program_requirement_qualification_round,
        lazy="dynamic",
        backref=app.db.backref("programs_requirement", lazy="dynamic"))

    def __repr__(self):
        return f"<ProgramRequirement {self.program.name} " \
            f"for scholarship {self.scholarship_id}>"

    def has_qualification_round(self, qualification_round):
        """Checks if program requirement has qualification round.

        Args:
            qualification_round (QualificationRound): qualification round.

        Returns:
            bool: True if program has qualification round, false otherwise.
        """
        return self.qualification_rounds.filter_by(
            id=qualification_round.id).count() > 0

    def add_qualification_round(self, qualification_round):
        """Adds qualification round to program requirement.

        Args:
            qualification_round (QualificationRound): qualification round
        """
        if not self.has_qualification_round(qualification_round):
            self.qualification_rounds.append(qualification_round)

    def remove_qualification_round(self, qualification_round):
        """Removes qualification round from program requirement.

        Args:
            qualification_round (QualificationRound): qualification round
        """
        if self.has_qualification_round(qualification_round):
            self.qualification_rounds.remove(qualification_round)

    def to_dict(self):
        return {
            "id": self.id,
            "links": {
                "get_program":
                flask.url_for("programs.get_program", id=self.program_id),
                "get_qualification_rounds":
                flask.url_for(
                    "scholarships.get_program_requirement_qualification_rounds",
                    scholarship_id=self.scholarship_id,
                    program_id=self.program_id)
            }
        }


class BooleanRequirement(app.db.Model, base_mixin.BaseMixin,
                         paginated_api_mixin.PaginatedAPIMixin):
    """Boolean requirement

    holds many to many relationship to the question table.

    Attributes:
        scholarship_id (integer): scholarship id.
        question_id (integer): question id.
        question (db.relationship): question relationship.
        required_value (boolean): value required to get scholarship.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    scholarship_id = app.db.Column("scholarship_id", app.db.Integer,
                                   app.db.ForeignKey("scholarship.id"))
    question_id = app.db.Column("question_id", app.db.Integer,
                                app.db.ForeignKey("question.id"))

    question = app.db.relationship("Question")
    required_value = app.db.Column(app.db.Boolean, default=True)

    def __repr__(self):
        return f"<Boolean requirement for {self.scholarship_id}>"

    def to_dict(self):
        return {
            "question_name": self.question.name,
            "required_value": self.required_value,
            "links": {
                "get_question":
                flask.url_for("questions.get_question", id=self.question_id)
            }
        }


class GradeRequirement(app.db.Model, base_mixin.BaseMixin,
                       paginated_api_mixin.PaginatedAPIMixin):
    """Grade requirement.

    Holds many to many relationship between grade group and grade.

    Attributes:
        id (integer): model id.
        grade_group_id (integer): grade_group id.
        grade_id (integer): grade id.
        grade (sqlalchemy.relationship): grade relationship.
        range_min (float): valid grade min.
        range_max (float): valid grade max.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    grade_requirement_group_id = app.db.Column(
        app.db.Integer, app.db.ForeignKey("grade_requirement_group.id"))
    grade_id = app.db.Column(app.db.Integer, app.db.ForeignKey("grade.id"))
    grade = app.db.relationship("Grade")
    range_min = app.db.Column(app.db.Numeric(8, 2), nullable=True)
    range_max = app.db.Column(app.db.Numeric(8, 2), nullable=True)

    def __repr__(self):
        return "<GradeRequirement for grade_requirement_group " \
            f"= {self.grade_requirement_group_id} and " \
            f"grade_id = {self.grade_id}>"

    @property
    def min(self):
        return self.range_min if self.range_min is not None else self.grade.min

    @min.setter
    def min(self, value):
        self.range_min = value

    @property
    def max(self):
        return self.range_max if self.range_max is not None else self.grade.max

    @max.setter
    def max(self, value):
        self.range_max = value

    def to_dict(self):
        return {
            "grade_name": self.grade.name,
            "grade_range_requirement": {
                "min": self.min,
                "max": self.max
            },
            "get_grade": flask.url_for("grades.get_grade", id=self.grade.id)
        }


selection_requirement_option = app.db.Table(
    "selection_requirement_option",
    app.db.Column("selection_requirement_id", app.db.Integer,
                  app.db.ForeignKey("selection_requirement.id")),
    app.db.Column("option_id", app.db.Integer, app.db.ForeignKey("option.id")))

selection_requirement_accepted_option = app.db.Table(
    "selection_requirement_accepted_option",
    app.db.Column("selection_requirement_id", app.db.Integer,
                  app.db.ForeignKey("selection_requirement.id")),
    app.db.Column("option_id", app.db.Integer, app.db.ForeignKey("option.id")))


class SelectionRequirement(app.db.Model, base_mixin.BaseMixin,
                           paginated_api_mixin.PaginatedAPIMixin):
    """
    Selection requirement association table model.

    id (integer): model id.
    scholarship_id (integer): scholarship id.
    question_id (integer): question id.
    question (SQLAlchemy.relationship): question relationship.
    options (SQLAlchemy.relationship):  options for question.
    accepted_options (SQLAlchemy.relationship): accepted options by the entity.
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    scholarship_id = app.db.Column(
        app.db.Integer, app.db.ForeignKey("scholarship.id"), nullable=False)
    question_id = app.db.Column(
        app.db.Integer, app.db.ForeignKey("question.id"), nullable=False)
    question = app.db.relationship("Question")
    options = app.db.relationship(
        "Option",
        secondary=selection_requirement_option,
        cascade="all, delete-orphan",
        lazy="dynamic",
        backref=app.db.backref("selection_requirements", lazy="dynamic"))

    accepted_options = app.db.relationship(
        "Option",
        secondary=selection_requirement_accepted_option,
        cascade="all, delete-orphan",
        lazy="dynamic",
        backref=app.db.backref(
            "accepted_selection_requirements", lazy="dynamic"))

    def __repr__(self):
        return f"<SelectionRequirement {self.id}>"

    def has_option(self, option):
        """
        Checks if selection requirement has option.

        Args:
            option: option to check.

        Returns:
            bool: True if requirement has option, False otherwise.
        """
        return self.options.filter(
            option_model.Option.id == option.id).count() > 0

    def add_option(self, option):
        """
        Adds option to selection requirement.

        Args:
            option: option to add.
        """

        if not self.has_option(option):
            self.options.append(option)

    def remove_option(self, option):
        """
        Removes option to selection requirement.

        Args:
            option: option to remove.
        """

        if self.has_option(option):
            self.options.remove(option)

    def has_accepted_option(self, option):
        """
        Checks if selection requirement has accepted option.

        Args:
            option: option to check.

        Returns:
            bool: True if requirement has option, False otherwise.
        """
        return self.accepted_options.filter(
            option_model.Option.id == option.id).count() > 0

    def add_accepted_option(self, option):
        """
        Adds accepted option to selection requirement.

        Args:
            option: option to add.
        """

        if self.has_option(option) and not self.has_accepted_option(option):
            self.accepted_options.append(option)

    def remove_accepted_option(self, option):
        """
        Removes accepted option to selection requirement.

        Args:
            option: option to remove.
        """

        if self.has_accepted_option(option):
            self.accepted_options.remove(option)

    def to_dict(self):

        return {
            "id": self.id,
            "links": {
                "get_question":
                flask.url_for("questions.get_question", id=self.option_id),
                "get_options":
                flask.url_for(
                    "scholarships.get_selection_requirement_option",
                    id=self.scholarship_id),
                "get_accepted_options":
                flask.url_for(
                    "scholarships.get_selection_requirement_accepted_option",
                    id=self.scholarship_id)
            }
        }
