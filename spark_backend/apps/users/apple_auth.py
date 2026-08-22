import jwt
import requests
from django.conf import settings
from django.core.cache import cache
from jwt import PyJWKClient, PyJWK

from .services import AuthError


class AppleTokenVerifier:
    JWKS_URL = "https://appleid.apple.com/auth/keys"
    CACHE_KEY = "apple_jwks"
    CACHE_TTL = 86400

    def _fetch_jwks(self) -> dict:
        jwks = cache.get(self.CACHE_KEY)
        if jwks is not None:
            return jwks
        response = requests.get(self.JWKS_URL, timeout=10)
        response.raise_for_status()
        jwks = response.json()
        cache.set(self.CACHE_KEY, jwks, self.CACHE_TTL)
        return jwks

    def _get_public_key(self, kid: str) -> PyJWK:
        jwks = self._fetch_jwks()
        for key_data in jwks.get("keys", []):
            if key_data.get("kid") == kid:
                return PyJWK(key_data)
        raise AuthError("Invalid Apple identity token: unknown kid.")

    def verify(self, identity_token: str) -> dict:
        try:
            header = jwt.get_unverified_header(identity_token)
        except Exception as e:
            raise AuthError(f"Invalid Apple identity token: {e}")

        kid = header.get("kid")
        if not kid:
            raise AuthError("Invalid Apple identity token: missing kid.")

        public_key = self._get_public_key(kid)
        rsa_key = public_key.key

        try:
            claims = jwt.decode(
                identity_token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.APPLE_BUNDLE_ID,
                issuer="https://appleid.apple.com",
            )
        except jwt.ExpiredSignatureError:
            raise AuthError("Apple identity token has expired.")
        except jwt.InvalidAudienceError:
            raise AuthError("Apple identity token has invalid audience.")
        except jwt.InvalidIssuerError:
            raise AuthError("Apple identity token has invalid issuer.")
        except Exception as e:
            raise AuthError(f"Invalid Apple identity token: {e}")

        return claims
