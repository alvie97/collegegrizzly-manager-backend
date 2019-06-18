"""Handles app security."""
from app.security.utils import (protect_blueprint, add_token_to_database,
                                get_user_tokens, is_token_revoked,
                                prune_database, revoke_all_user_tokens,
                                revoke_token, unrevoke_token)
