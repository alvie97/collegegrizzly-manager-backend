from datetime import datetime, timedelta
from time     import time
from flask    import current_app, url_for
from app      import db, photos
from .common  import PaginatedAPIMixin

class Picture(PaginatedAPIMixin, db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    public_id   = db.Column(db.String(50), unique=True)
    name        = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow)
    type        = db.Column(db.String(256), default='campus')
    college_id  = db.Column(db.Integer, db.ForeignKey('college.id'))

    ATTR_FIELDS = [
        'type'
    ]

    def __repr__(self):
        return '<Picture {}>'.format(self.name)

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'name': self.name,
            'path': photos.url(self.name),
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'type': self.type
        }

    def from_dict(self, data):
        for field in self.ATTR_FIELDS:
            if field in data:
                setattr(self, field, data[field])

        self.updated_at = datetime.utcnow()
