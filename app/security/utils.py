import functools

import flask
import flask_jwt_extended
import datetime

import app
from app.api import errors
from app.models import token_blacklist


def add_token_to_database(token):
    """
    Adds a new token to the database. It is not revoked when it is added.

    Args:
        token (string): enconded token.
    """
    decoded_token = flask_jwt_extended.decode_token(token)
    jti = decoded_token["jti"]
    user = decoded_token[flask.current_app.config["JWT_IDENTITY_CLAIM"]]
    expires = datetime.datetime.fromtimestamp(decoded_token["exp"])

    db_token = token_blacklist.TokenBlacklist(
        jti=jti,
        user=user,
        expires=expires,
    )
    app.db.session.add(db_token)
    app.db.session.commit()


@app.jwt.token_in_blacklist_loader
def is_token_revoked(token):
    """
    Checks if token is revoked or not. If token is not in the database
    it is considered revoked.

    Args:
        token: decoded token to check.
    """

    jti = token["jti"]

    token = token_blacklist.TokenBlacklist.query.filter_by(jti=jti).first()

    if token is None:
        return True

    return token.revoked


def protect_blueprint(blueprint):
    """
    applies login decorators to blueprint routes
    """

    @blueprint.before_request
    @flask_jwt_extended.jwt_required
    def before_request():
        pass


def get_user_tokens(user):
    """
    returns all user tokens.

    Args:
        user (string): user identity.
    """
    return token_blacklist.TokenBlacklist.query.filter_by(user=user).all()


def revoke_all_user_tokens(user):
    """
    revokes all unrevoked user tokens

    Args:
        user (string): user identity
    """

    tokens = token_blacklist.TokenBlacklist.query.filter_by(
        user=user, revoked=False).all()

    for token in tokens:
        revoke_token(token)


def revoke_token(token):
    """
    Revokes token.

    Args:
        token (TokenBlacklist): token to revoke
    """
    token.revoked = True


def unrevoke_token(token):
    """
    Revokes token.

    Args:
        token (TokenBlacklist): token to unrevoke
    """
    token.unrevoked = True


def prune_database():
    """
    Delete all expired tokens from database
    """

    now = datetime.datetime.now()
    expired = token_blacklist.TokenBlacklist.query.filter(
        token_blacklist.TokenBlacklist.expires < now).all()

    for token in expired:
        app.db.session.delete(token)
    app.db.session.commit()