from datetime import datetime, timedelta

from app import db
from .common.base_mixin import BaseMixin
from config import Config

from flask import current_app


class RefreshToken(db.Model, BaseMixin):
    __tablename__ = "refresh_token"
    token = db.Column(db.String(256), primary_key=True)
    issued_at = db.Column(db.DateTime(), default=datetime.utcnow())
    expires_at = db.Column(
        db.DateTime(),
        default=datetime.utcnow() + Config.REFRESH_TOKEN_DURATION)
    access_token_jti = db.Column(db.String(512))
    user_id = db.Column(db.String(256))
    revoked = db.Column(db.Boolean(), default=False)
    __str_repr__ = "refresh_token"

    def __repr__(self):
        return f"<Token {self.token}>"

    def check_user(self, user_id):
        return self.user_id == user_id

    def has_expired(self):
        return self.expires_at < datetime.utcnow()

    def is_valid(self):
        return not (self.has_expired() or self.revoked)

    def is_jti_valid(self, jti):
        return self.access_token_jti == jti
