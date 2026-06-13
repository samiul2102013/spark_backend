from datetime import datetime

from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


def blacklist_refresh_token(refresh_str: str) -> None:
    try:
        token = RefreshToken(refresh_str)
        jti = token.payload.get("jti")
        exp = token.payload.get("exp")
        if jti and exp:
            ttl = max(int(exp - datetime.now().timestamp()), 0)
            cache.set(f"bl:{jti}", "1", timeout=ttl)
    except TokenError:
        pass


def is_token_blacklisted(refresh_str: str) -> bool:
    try:
        token = RefreshToken(refresh_str)
        jti = token.payload.get("jti")
        if jti and cache.get(f"bl:{jti}"):
            return True
    except TokenError:
        pass
    return False
