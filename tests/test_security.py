import app as application
from app import security, utils
from app.models import token_blacklist
from app.models import user as user_model
import time
import flask_jwt_extended


def test_token_to_database(app):
    """
    Tests add_token_to_database function
    """
    with app.app_context():
        token = flask_jwt_extended.create_access_token("test")
        security.add_token_to_database(token)
        application.db.session.commit()
        jti = flask_jwt_extended.decode_token(token)["jti"]
        assert token_blacklist.TokenBlacklist.query.filter_by(
            jti=jti).count() == 1


def test_is_token_revoked(app, token):
    """
    tests is_token_revoked function
    """

    with app.app_context():
        token_obj = token_blacklist.TokenBlacklist.query.first()
        decoded_token = flask_jwt_extended.decode_token(token)
        assert security.is_token_revoked(decoded_token) == False
        token_obj.revoked = True
        application.db.session.commit()
        assert security.is_token_revoked(decoded_token) == True


def test_get_user_tokens(app, user):
    """
    tests get_user_tokens function
    """
    with app.app_context():
        user_obj = user_model.User.query.first()
        encoded_token = flask_jwt_extended.create_access_token(
            user_obj.username)
        security.add_token_to_database(encoded_token)
        application.db.session.commit()
        decoded_token = flask_jwt_extended.decode_token(encoded_token)
        user_tokens = security.get_user_tokens(user_obj.username)
        assert len(user_tokens) == 1
        assert user_tokens[0].jti == decoded_token["jti"]


def test_revoke_all_user_tokens(app, user):
    """
    tests revoke_all_user_tokens function
    """
    with app.app_context():
        user_obj = user_model.User.query.first()
        for i in range(5):
            encoded_token = flask_jwt_extended.create_access_token(
                user_obj.username)
            security.add_token_to_database(encoded_token)
            application.db.session.commit()
        security.revoke_all_user_tokens(user_obj.username)
        application.db.session.commit()
        assert len(user_tokens) == 5
        for token in user_tokens:
            assert token.revoked == False
        user_tokens = security.get_user_tokens(user_obj.username)
        assert len(user_tokens) == 5
        for token in user_tokens:
            assert token.revoked == True


def test_revoke_token(app, token):
    """
    tests revoke_token function
    """
    with app.app_context():
        token_obj = token_blacklist.TokenBlacklist.query.first()
        assert token_obj.revoked == False
        security.revoke_token(token_obj)
        application.db.session.commit()
        assert token_obj.revoked == True


def test_unrevoke_token(app, token):
    """
    tests unrevoke_token function
    """
    with app.app_context():
        token_obj = token_blacklist.TokenBlacklist.query.first()
        security.revoke_token(token_obj)
        application.db.session.commit()
        assert token_obj.revoked == True
        security.unrevoke_token(token_obj)
        application.db.session.commit()
        assert token_obj.revoked == False


def test_prune_database(app, user):
    """
    test prune_database function
    """

    with app.app_context():
        user_obj = user_model.User.query.first()
        for i in range(5):
            encoded_token = flask_jwt_extended.create_access_token(
                user_obj.username)
            security.add_token_to_database(encoded_token)
            application.db.session.commit()

        time.sleep(4)
        encoded_token = flask_jwt_extended.create_access_token(
            user_obj.username)
        security.add_token_to_database(encoded_token)
        application.db.session.commit()
        assert token_blacklist.TokenBlacklist.query.count() == 6
        security.prune_database()
        application.db.session.commit()
        assert token_blacklist.TokenBlacklist.query.count() == 1


def test_protect_blueprint(app, client):
    """
    tests protect_blueprint function
    """

    url = "/api/colleges/"
    response = client.get(url)
    assert response.status_code == 422
    assert response.get_json()["message"] == "invalid token"