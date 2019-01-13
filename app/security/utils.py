from .token_auth.utils import get_access_token_from_cookie


def get_current_user():
    """
    Returns the current user
    """

    try:
        access_token = get_access_token_from_cookie()
    except KeyError:
        return None

    try:
        jwt_claims = decode_jwt(access_token, current_app.config["JWT_SECRET"],
                                current_app.config["JWT_ALGORITHM"])

    except jwt.exceptions.ExpiredSignatureError:

        jwt_claims = decode_jwt(
            access_token,
            current_app.config["JWT_SECRET"],
            current_app.config["JWT_ALGORITHM"],
            options={"verify_exp": False})

    except jwt.exceptions.InvalidTokenError:
        return None

    try:
        return jwt_claims.user_id
    except KeyError:
        return None
