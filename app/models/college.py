import hashlib
import flask

import app
from app import utils

from app.models.common import base_mixin
from app.models.common import date_audit
from app.models.common import paginated_api_mixin


class College(app.db.Model, paginated_api_mixin.PaginatedAPIMixin,
              date_audit.DateAudit, base_mixin.BaseMixin):
    """College model.

    Attributes:
        id (Integer): model id.
        name (String): name of the college.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    str_repr = "college"
    college_details = app.db.relationship(
        "CollegeDetails",
        uselist=False,
        backref="college",
        cascade="all, delete-orphan")

    ATTR_FIELDS = ["name"]

    def __repr__(self):
        return f"<College {self.college_details.name}>"

    def for_pagination(self):
        return {
            "name": self.college_details.name,
            "audit_dates": self.audit_dates(),
            "links": {
                "get_college": flask.url_for(
                    "colleges.get_college", id=self.id)
            }
        }

    def to_dict(self):
        return {
            "id": self.id,
            "details": self.college_details.to_dict(),
            "links": {}
        }
