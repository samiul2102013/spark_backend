import json
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from django.test import override_settings

from apps.users.apple_auth import AppleTokenVerifier
from apps.users.services import AuthError, AuthService

User = __import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model()

JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISS = "https://appleid.apple.com"


def _generate_rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_private, pem_public


def _public_key_to_jwks(pem_public, kid="testkey1"):
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    from cryptography.hazmat.backends import default_backend
    from base64 import urlsafe_b64encode

    pub = load_pem_public_key(pem_public, backend=default_backend())
    pub_num = pub.public_numbers()

    def _b64(n):
        length = (n.bit_length() + 7) // 8
        return urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()

    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": kid,
                "use": "sig",
                "alg": "RS256",
                "n": _b64(pub_num.n),
                "e": _b64(pub_num.e),
            }
        ]
    }


def _sign_identity_token(pem_private, sub="test-apple-sub-001", aud=None, iss=None, exp_delta=None, kid="testkey1"):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "aud": aud or settings.APPLE_BUNDLE_ID,
        "iss": iss or APPLE_ISS,
        "exp": int((now + (exp_delta or timedelta(hours=1))).timestamp()),
        "iat": int(now.timestamp()),
        "email": "appleuser@privaterelay.appleid.com",
        "email_verified": True,
        "is_private_email": True,
    }
    headers = {"kid": kid}
    return pyjwt.encode(payload, pem_private, algorithm="RS256", headers=headers)


@pytest.fixture
def rsa_keypair():
    return _generate_rsa_keypair()


@pytest.fixture
def valid_token(rsa_keypair):
    priv, pub = rsa_keypair
    return _sign_identity_token(priv)


@pytest.fixture
def jwks_response(rsa_keypair):
    priv, pub = rsa_keypair
    return _public_key_to_jwks(pub)


@pytest.mark.django_db
class TestAppleTokenVerifier:

    def test_verify_success(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        token = _sign_identity_token(priv)
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            verifier = AppleTokenVerifier()
            claims = verifier.verify(token)
        assert claims["sub"] == "test-apple-sub-001"
        assert claims["email"] == "appleuser@privaterelay.appleid.com"
        assert claims["email_verified"] is True
        assert claims["is_private_email"] is True

    def test_verify_expired_token(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        token = _sign_identity_token(priv, exp_delta=timedelta(hours=-1))
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            verifier = AppleTokenVerifier()
            with pytest.raises(AuthError, match="has expired"):
                verifier.verify(token)

    def test_verify_wrong_audience(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        token = _sign_identity_token(priv, aud="com.wrong.bundle")
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            verifier = AppleTokenVerifier()
            with pytest.raises(AuthError, match="invalid audience"):
                verifier.verify(token)

    def test_verify_wrong_issuer(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        token = _sign_identity_token(priv, iss="https://fake.issuer.com")
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            verifier = AppleTokenVerifier()
            with pytest.raises(AuthError, match="invalid issuer"):
                verifier.verify(token)

    def test_verify_bad_signature(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        other_priv, _ = _generate_rsa_keypair()
        token = _sign_identity_token(other_priv)
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            verifier = AppleTokenVerifier()
            with pytest.raises(AuthError, match="Invalid Apple identity token"):
                verifier.verify(token)

    def test_verify_unknown_kid(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        token = _sign_identity_token(priv, kid="unknown-kid")
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            verifier = AppleTokenVerifier()
            with pytest.raises(AuthError, match="unknown kid"):
                verifier.verify(token)


@pytest.mark.django_db
class TestAppleLoginService:

    def test_apple_login_creates_user(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        token = _sign_identity_token(priv)
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            service = AuthService()
            result = service.apple_login(identity_token=token, full_name="Jane Appleseed")
        assert "access" in result
        assert "refresh" in result
        assert result["user"]["full_name"] == "Jane Appleseed"
        assert result["user"]["role"] == "resident"
        assert User.objects.filter(apple_user_id="test-apple-sub-001").exists()

    def test_apple_login_duplicate_finds_existing(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        token = _sign_identity_token(priv)
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            service = AuthService()
            result1 = service.apple_login(identity_token=token)
        user_count = User.objects.count()
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            service = AuthService()
            result2 = service.apple_login(identity_token=token)
        assert User.objects.count() == user_count
        assert result2["user"]["phone_number"] == result1["user"]["phone_number"]
        assert result2["access"] != result1["access"]

    def test_apple_login_defaults_full_name(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        token = _sign_identity_token(priv)
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            service = AuthService()
            result = service.apple_login(identity_token=token)
        assert result["user"]["full_name"] == "Apple User"

    def test_apple_login_synthetic_phone_pattern(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        token = _sign_identity_token(priv)
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            service = AuthService()
            result = service.apple_login(identity_token=token)
        phone = result["user"]["phone_number"]
        assert phone.startswith("apple-")
        assert len(phone) == 6 + 12
        user = User.objects.get(apple_user_id="test-apple-sub-001")
        assert user.phone_number == phone

    def test_apple_login_without_email(self, rsa_keypair, jwks_response):
        priv, pub = rsa_keypair
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "sub-no-email",
            "aud": settings.APPLE_BUNDLE_ID,
            "iss": APPLE_ISS,
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "iat": int(now.timestamp()),
        }
        headers = {"kid": "testkey1"}
        token = pyjwt.encode(payload, priv, algorithm="RS256", headers=headers)
        with patch.object(AppleTokenVerifier, "_fetch_jwks", return_value=jwks_response):
            service = AuthService()
            result = service.apple_login(identity_token=token)
        user = User.objects.get(apple_user_id="sub-no-email")
        assert user.email is None

    def test_auth_error_on_invalid_token(self, rsa_keypair, jwks_response):
        with pytest.raises(AuthError):
            service = AuthService()
            service.apple_login(identity_token="garbage-token")

    def test_synthetic_phone_not_colliding_with_e164(self):
        import re
        phone = f"apple-{uuid.uuid4().hex[:12]}"
        assert not phone.startswith("+")
        assert not re.match(r"^\d+$", phone)
