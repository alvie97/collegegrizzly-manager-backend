from .common.paginated_api_mixin import PaginatedAPIMixin
from .common.base_mixin import BaseMixin
from .common.date_audit import DateAudit

from app import db
from datetime import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash


class User(PaginatedAPIMixin, BaseMixin, DateAudit, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), index=True, unique=True)
    username = db.Column(db.String(120), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_session = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(256), default="basic")

    ATTR_FIELDS = ["email", "role"]

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
            "last_session": self.last_session.isoformat() + "Z"
        }
