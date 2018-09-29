from .common.paginated_api_mixin import PaginatedAPIMixin
from .common.date_audit import DateAudit
from app import db, photos
from datetime import datetime
import os

class Picture(PaginatedAPIMixin, DateAudit, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.String(50), unique=True)
  name = db.Column(db.Text)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow)
  type = db.Column(db.String(256), default="campus")
  college_id = db.Column(db.Integer, db.ForeignKey("college.id"))

  ATTR_FIELDS = ["type"]

  def __repr__(self):
    return "<Picture {}>".format(self.name)

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

  # TODO: see if BaseMixin can be used here
  def update(self, data):
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field].lower()
                if field == "type" else data[field])
