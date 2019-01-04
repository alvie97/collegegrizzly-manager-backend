from app import db
from datetime import datetime


class DateAudit(object):

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def audit_dates(self) -> dict:
        """
    Returns date properties for audit
    """
        return {
            "created_at": self.created_at.isoformat() + 'Z',
            "updated_at": self.updated_at.isoformat() + 'Z'
        }
