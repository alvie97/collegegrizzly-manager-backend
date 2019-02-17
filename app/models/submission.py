from datetime import datetime

from flask import url_for

from app import db
from app.common.utils import generate_public_id

from .common.base_mixin import BaseMixin
from .common.date_audit import DateAudit
from .common.paginated_api_mixin import PaginatedAPIMixin


class Submission(db.Model, PaginatedAPIMixin, DateAudit, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(
        db.String(50), unique=True, default=generate_public_id)
    reviewed_by_moderator_at = db.Column(db.DateTime, nullable=True)
    reviewed_by_admin_at = db.Column(db.DateTime, nullable=True)
    reviewed_by_moderator = db.Column(db.String(256), nullable=True)
    reviewed_by_admin = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(256), default="pending:")
    college_name = db.Column(db.String(256), nullable=True)
    submitted_by = db.Column(db.String(256), nullable=True)
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    __str_repr__ = "submission"

    def __repr__(self):
        return f"<Submission {self.public_id}"

    def for_pagination(self):
        return {
            "public_id": self.public_id,
            "review_details": {
                "moderator": {
                    "username":
                    self.reviewed_by_moderator,
                    "reviewed_at":
                    self.reviewed_by_moderator_at.isoformat() + 'Z'
                    if self.reviewed_by_moderator is not None else None
                },
                "administrator": {
                    "username":
                    self.reviewed_by_admin,
                    "reviewed_at":
                    self.reviewed_by_admin_at.isoformat() + 'Z'
                    if self.reviewed_by_admin is not None else None
                }
            },
            **self.audit_dates(), "status": self.status,
            "college_name": self.college_name,
            "submited_by": self.submitted_by,
            "_links": {
                "get_college":
                url_for("colleges.get_college", public_id=self.public_id),
                "get_user":
                url_for("users.get_user", username=self.user.username)
            }
        }

    def to_dict(self):
        return self.for_pagination()
