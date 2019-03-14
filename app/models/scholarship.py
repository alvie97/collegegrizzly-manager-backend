import flask
import app

from app.models.common import base_mixin
from app.models.common import date_audit
from app.models.common import paginated_api_mixin
from app.models import scholarship_details
from app.models import association_tables


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
        details = scholarship_details.ScholarshipDetails.ATTR_FIELDS
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

    def for_pagination(self):
        """ Serializes model for pagination.

        Returns:
            Dict: returns serialized object for pagination.
        """
        return {
            "id": self.id,
            "name": self.scholarship_details.name,
            "audit_dates": self.audit_dates(),
            "links": {}
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
