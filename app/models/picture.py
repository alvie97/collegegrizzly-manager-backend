import os
from datetime import datetime

from app import db, photos
from app.utils import generate_public_id

from .common.base_mixin import BaseMixin
from .common.date_audit import DateAudit
from .common.paginated_api_mixin import PaginatedAPIMixin


class Picture(PaginatedAPIMixin, BaseMixin, DateAudit, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(
        db.String(50), unique=True, default=generate_public_id)
    name = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(256), default="campus")
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"))
    __str_repr__ = "picture"

    ATTR_FIELDS = ["type"]

    def __repr__(self):
        return f"<Picture {self.name}>"

    def delete(self):
        try:
            os.remove(photos.path(self.name))
            db.session.delete(self)
        except OSError:
            pass

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "public_id": self.public_id,
            "name": self.name,
            "path": photos.url(self.name),
            "audit_dates": self.audit_dates(),
            "type": self.type
        }
