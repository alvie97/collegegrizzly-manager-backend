from datetime import datetime

from flask import url_for

from app import db
from app.utils import generate_public_id

from .common.base_mixin import BaseMixin
from .common.date_audit import DateAudit
from .common.paginated_api_mixin import PaginatedAPIMixin


class Submission(db.Model, PaginatedAPIMixin, DateAudit, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(
        db.String(50), unique=True, default=generate_public_id)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    assigned_to = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(256), default="pending")
    college_name = db.Column(db.String(256), nullable=True)
    submitted_by = db.Column(db.String(256), nullable=True)
    observation = db.Column(db.Text(), nullable=True)
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    __str_repr__ = "submission"

    ATTR_FIELDS = ["reviewed_at", "reviewed_by", "status", "college_name"]

    def __repr__(self):
        return f"<Submission {self.public_id}"

    def for_pagination(self):
        return {
            "public_id": self.public_id,
            "review_details": {
                "status":
                self.status,
                "reviewed_at":
                self.reviewed_at.isoformat() + 'Z'
                if self.status != "pending" else None,
                "observation":
                self.observation
            },
            **self.audit_dates(), "assigned_to": self.assigned_to,
            "college_name": self.college_name,
            "submitted_by": self.submitted_by,
            "_links": {
                "get_college":
                url_for("colleges.get_college", public_id=self.public_id),
                "get_user":
                url_for("users.get_user", username=self.user.username)
            }
        }

    def to_dict(self):
        return self.for_pagination()
