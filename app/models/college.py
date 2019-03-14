import hashlib
import flask

import app
from app import utils

from app.models.common import base_mixin
from app.models.common import date_audit
from app.models.common import paginated_api_mixin
from app.models import association_tables
from app.models import major as major_model
from app.models import college_details


class College(app.db.Model, paginated_api_mixin.PaginatedAPIMixin,
              date_audit.DateAudit, base_mixin.BaseMixin):
    """College model.

    Attributes:
        id (Integer): model id.
        college_details (sqlalchemy.Model): college details.
        majors (sqlachemy.Query): college majors
        additional_details (sqlalchemy.relationship): list of additional details.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    str_repr = "college"
    college_details = app.db.relationship(
        "CollegeDetails",
        uselist=False,
        backref="college",
        cascade="all, delete-orphan")

    additional_details = app.db.relationship(
        "Detail",
        backref="college",
        cascade="all, delete-orphan",
        lazy="dynamic")

    majors = app.db.relationship(
        "Major",
        secondary=association_tables.college_major,
        lazy="dynamic",
        backref=app.db.backref("colleges", lazy="dynamic"))

    scholarships = app.db.relationship(
        "Scholarship",
        backref="college",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    ATTR_FIELDS = ["name"]

    def __repr__(self):
        return f"<College {self.college_details.name}>"

    def has_major(self, major_id):
        """checks if college has major.

        Args:
            self (class): college class.
            major_id (integer): major id.
        Returns:
            Boolean: true if college has major, false otherwise.

        """
        return self.majors.filter(major_model.Major.id == major_id).count() > 0

    def add_major(self, major):
        """Adds major to college.

        Args:
            self (class): college class.
            major (sqlalchemy.Model): major object.
        """
        if not self.has_major(major.id):
            self.majors.append(major)

    def remove_major(self, major):
        """Removes major to college.

        Args:
            self (class): college class.
            major (sqlalchemy.Model): major object.
        """
        if self.has_major(major.id):
            self.majors.remove(major)

    def get_additional_details(self):
        """Retrives addtional college details.

        Args:
            self (class): college class.
        Returns:
            list: additional college details.
        """
        return [detail.to_dict() for detail in self.additional_details.all()]

    def has_detail(self, detail_name):
        """checks if college has additional detail.

        Args:
            self (class): college class.
            detail_name (string): detail name.
        Returns:
            Boolean: true if college has major, false otherwise.

        """
        return detail_name not in college_details.CollegeDetails.ATTR_FIELDS \
            and self.additional_details.filter_by(name=detail_name).count() > 0

    def add_additional_detail(self, detail):
        """Adds additional detail to college.

        Args:
            self (class): college class.
            detail (sqlalchemy.Model): detail object.
        """
        if not self.has_detail(detail.name):
            self.additional_details.append(detail)

    def remove_additional_detail(self, detail):
        """Removes additional detail to college.

        Args:
            self (class): college class.
            detail (sqlalchemy.Model): detail object.
        """
        if self.has_detail(detail.name):
            self.additional_details.remove(detail)

    def for_pagination(self):
        """ Serializes model for pagination.

        Returns:
            Dict: returns serialized object for pagination.
        """
        return {
            "name": self.college_details.name,
            "audit_dates": self.audit_dates(),
            "links": {
                "get_college": flask.url_for(
                    "colleges.get_college", id=self.id)
            }
        }

    def to_dict(self):
        """ Serializes model.

        Returns:
            Dict: returns serialized object.
        """
        return {
            "id": self.id,
            "details": self.college_details.to_dict(),
            "audit_dates": self.audit_dates(),
            "links": {
                "get_majors": flask.url_for("colleges.get_majors", id=self.id)
            }
        }
