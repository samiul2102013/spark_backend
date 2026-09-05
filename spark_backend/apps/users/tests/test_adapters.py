from django.test import SimpleTestCase, override_settings

from apps.users.adapters import SMSAdapter


@override_settings(PHONE_COUNTRY_CODE="+880")
class TestToE164WithBangladeshCountryCode(SimpleTestCase):
    def test_leading_zero_bangladeshi_number(self):
        assert SMSAdapter._to_e164("01521584710") == "+8801521584710"

    def test_without_leading_zero_bangladeshi_number(self):
        assert SMSAdapter._to_e164("1521584710") == "+8801521584710"

    def test_already_e164_is_preserved(self):
        assert SMSAdapter._to_e164("+8801521584710") == "+8801521584710"

    def test_already_e164_us_is_preserved(self):
        assert SMSAdapter._to_e164("+12125551234") == "+12125551234"

    def test_e164_without_plus_bangladeshi_number(self):
        assert SMSAdapter._to_e164("8801521584710") == "+8801521584710"

    def test_us_eleven_digit_number(self):
        assert SMSAdapter._to_e164("12125551234") == "+12125551234"

    def test_leading_001_prefix(self):
        assert SMSAdapter._to_e164("0012125551234") == "+12125551234"


@override_settings(PHONE_COUNTRY_CODE="+1")
class TestToE164WithUsCountryCode(SimpleTestCase):
    def test_us_eleven_digit_number(self):
        assert SMSAdapter._to_e164("12125551234") == "+12125551234"

    def test_already_e164_is_preserved(self):
        assert SMSAdapter._to_e164("+15855669533") == "+15855669533"