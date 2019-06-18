from datetime import datetime, timedelta

from flask import current_app

from app import db
from config import Config

from .common.base_mixin import BaseMixin


class TokenBlacklist(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    user = db.Column(db.String(256), nullable=False)
    revoked = db.Column(db.Boolean(), default=False)
    expires = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Token {self.jti}>"

    def to_dict(self):
        return {
            "jti": self.jti,
            "user": self.user,
            "revoked": self.revoked,
            "expires": self.expires.isoformat() + 'Z'
        }