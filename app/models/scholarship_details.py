from .common.base_mixin import BaseMixin
from .common.date_audit import DateAudit
from app import db


class ScholarshipDetails(db.Model, BaseMixin, DateAudit):
    id = db.Column(db.Integer, primary_key=True)
    scholarship_id = db.Column(db.Integer, db.ForeignKey("scholarship.id"))

    def __repr__(self):
        return f"<Scholarship details for scholarship {self.scholarship.name}"

    def to_dict(self):

        return {"created_at": self.created_at, "updated_at": self.updated_at}
