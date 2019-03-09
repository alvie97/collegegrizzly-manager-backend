import flask
import app

from app import utils

from app.models.common import base_mixin
from app.models.common import date_audit
from app.models.common import paginated_api_mixin


class Scholarship(app.db.Model, paginated_api_mixin.PaginatedAPIMixin,
                  date_audit.DateAudit, base_mixin.BaseMixin):
    """Scholarship model

    Attributes:
        id (integer): model id.
        scholarship_details (SQLAlchemy.relationship): scholarship details.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    exclude_from_match = app.db.Column(app.db.Boolean, default=False)
    scholarship_details = app.db.relationship(
        "ScholarshipDetails",
        uselist=False,
        backref="scholarship",
        cascade="all, delete-orphan")
    str_repr = "scholarship"

    def __repr__(self):
        return f"<Scholarship {self.id}>"

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
