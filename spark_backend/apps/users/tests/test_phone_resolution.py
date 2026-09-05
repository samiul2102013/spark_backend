from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings

from apps.users.adapters import SMSAdapter
from apps.users.services import AuthError, AuthService
from apps.users.utils import resolve_user_by_phone

User = get_user_model()

PHONE_SETTINGS = dict(
    PHONE_COUNTRY_CODE="+880",
    OTP_MOCK_MODE=False,
    DEMO_PHONE_NUMBER="+10000000000",
    DEMO_OTP_CODE="000000",
)


def _create(phone, role="resident", password="testpass123"):
    return User.objects.create_user(
        phone_number=phone,
        full_name="Test User",
        role=role,
        password=password,
    )


@override_settings(**PHONE_SETTINGS)
class TestResolveUserByPhone(TestCase):
    def test_finds_stored_e164_given_raw_input(self):
        _create("+8801521584710")
        user = resolve_user_by_phone("01521584710")
        assert user is not None
        assert user.phone_number == "+8801521584710"

    def test_finds_stored_e164_given_e164_input(self):
        _create("+8801521584710")
        user = resolve_user_by_phone("+8801521584710")
        assert user is not None

    def test_finds_raw_stored_user_given_raw_input(self):
        _create("01856669533")
        user = resolve_user_by_phone("01856669533")
        assert user is not None
        assert user.phone_number == "01856669533"

    def test_finds_raw_stored_user_given_normalized_input(self):
        _create("01521584710")
        user = resolve_user_by_phone("+8801521584710")
        assert user is not None
        assert user.phone_number == "01521584710"

    def test_returns_none_when_missing(self):
        assert resolve_user_by_phone("01999999999") is None


@override_settings(**PHONE_SETTINGS)
class TestPhoneFlows(TestCase):
    def test_register_stores_normalized_phone(self):
        result = AuthService().register(
            phone="01856669533",
            full_name="John Doe",
            latitude=18.1096,
            longitude=-77.2975,
        )
        assert result["user_id"] == "+8801856669533"
        assert User.objects.filter(phone_number="+8801856669533").exists()

    def test_register_rejects_duplicate_of_raw_stored_user(self):
        _create("01521584710")
        with self.assertRaises(AuthError):
            AuthService().register(
                phone="01521584710",
                full_name="Dup",
                latitude=18.1,
                longitude=-77.2,
            )

    @patch.object(SMSAdapter, "send_otp")
    def test_otp_roundtrip_works_for_raw_stored_user(self, mock_send):
        user = _create("01856669533")
        service = AuthService()
        code_key = "+8801856669533"

        result = service.send_otp("01856669533")
        assert result["message"] == "OTP sent"
        code = cache.get(f"otp:{code_key}")
        assert code is not None

        resp = service.verify_otp("01856669533", code)
        assert resp["user"]["phone_number"] == user.phone_number
        assert User.objects.get(pk=user.pk).is_active is True

    @patch.object(SMSAdapter, "send_otp")
    def test_forgot_password_roundtrip_works_for_raw_stored_user(self, mock_send):
        _create("01521584710")
        service = AuthService()
        code_key = "+8801521584710"

        result = service.forgot_password("01521584710")
        assert result["message"] == "Reset code sent."
        code = cache.get(f"otp:{code_key}")
        assert code is not None

        resp = service.verify_reset_otp("01521584710", code)
        assert "access" in resp

    def test_login_with_raw_phone_finds_normalized_stored_user(self):
        from apps.users.authentication import authenticate

        _create("+8801521584710")
        user = authenticate("01521584710", "testpass123")
        assert user is not None
        assert user.phone_number == "+8801521584710"

    def test_login_with_raw_phone_finds_raw_stored_user(self):
        from apps.users.authentication import authenticate

        user = _create("01521584710")
        assert authenticate("01521584710", "testpass123") == user

    def test_login_invalid_credentials_returns_none(self):
        from apps.users.authentication import authenticate

        _create("+8801521584710")
        assert authenticate("01521584710", "wrongpass") is None
        assert authenticate("01999999999", "testpass123") is None