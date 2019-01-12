from datetime import datetime, timedelta

from app import db
from .common.base_mixin import BaseMixin

from flask import current_app


class RefreshToken(db.Model, BaseMixin):
    __tablename__ = "refresh_token"
    token = db.Column(db.String(256), primary_key=True)
    issued_at = db.Column(db.DateTime(), default=datetime.utcnow())
    expires_at = db.Column(
        db.DateTime(),
        default=datetime.utcnow() +
        current_app.config["REFRESH_TOKEN_DURATION"])
    access_token_jti = db.Column(db.String(512))
    user_id = db.Column(db.String(256))
    revoked = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return f"<Token {self.token}>"

    def check_user(self, user_id):
        return self.user_id == user_id

    def has_expired(self):
        return self.expires_at < datetime.utcnow()

    def is_valid(self):
        return not (self.has_expired() or self.revoked)

    def is_jti_valid(self, jti):
        return self.access_token_jti != jti

    @classmethod
    def revoke_token(cls, token="", instance=None):
        _token = None

        if instance is not None:
            _token = instance
        else:
            _token = cls.first(token=token)

        if _token is not None and _token.is_valid():
            _token.revoked = True

    @classmethod
    def revoke_user_tokens(cls, refresh_token):

        cls.update().where(cls.user_id == refresh_token.user_id,
                           cls.expires_at > datetime.utcnow(),
                           cls.revoked == False).values(revoked=True)
