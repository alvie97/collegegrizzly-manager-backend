from datetime import datetime
from werkzeug import security

import app
from app.models.common import base_mixin, date_audit, paginated_api_mixin


class User(paginated_api_mixin.PaginatedAPIMixin, base_mixin.BaseMixin,
           date_audit.DateAudit, app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    username = app.db.Column(app.db.String(120), index=True, unique=True)
    email = app.db.Column(app.db.String(120), index=True, unique=True)
    password_hash = app.db.Column(app.db.String(128))
    first_name = app.db.Column(app.db.String(256))
    last_name = app.db.Column(app.db.String(256))
    last_session = app.db.Column(app.db.DateTime, default=datetime.utcnow)
    role = app.db.Column(app.db.String(256), default="basic")
    submissions = app.db.relationship(
        "Submission", backref="user", lazy="dynamic")

    ATTR_FIELDS = ["first_name", "last_name", "email", "role"]

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = security.generate_password_hash(password)

    def check_password(self, password):
        return security.check_password_hash(self.password_hash, password)

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "audit_dates": self.audit_dates(),
            "last_session": self.last_session.isoformat() + "Z"
        }
