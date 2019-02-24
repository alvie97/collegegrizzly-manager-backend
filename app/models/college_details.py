from app import db

from .common.base_mixin import BaseMixin
from .common.date_audit import DateAudit


class CollegeDetails(db.Model, DateAudit, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(256), nullable=True)
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"))
    __str_repr__ = "college_details"

    ATTR_FIELDS = ["status"]

    def __repr__(self):
        return f"<College Details for college {self.college.id}>"

    def to_dict(self):
        return {
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
