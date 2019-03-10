import flask
import app

from app import utils

from app.models.common import base_mixin
from app.models.common import date_audit
from app.models.common import paginated_api_mixin
from app.models import scholarship_details


class Scholarship(app.db.Model, paginated_api_mixin.PaginatedAPIMixin,
                  date_audit.DateAudit, base_mixin.BaseMixin):
    """Scholarship model

    Attributes:
        id (integer): model id.
        scholarship_details (SQLAlchemy.relationship): scholarship details.
        additional_details (SQLAlchemy.relationship): additional scholarship details.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    exclude_from_match = app.db.Column(app.db.Boolean, default=False)
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
        return detail_name not in scholarship_details.ScholarshipDetails.ATTR_FIELDS \
               and self.additional_details.filter_by(name=detail_name).count() > 0

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
            "links": {}
        }
