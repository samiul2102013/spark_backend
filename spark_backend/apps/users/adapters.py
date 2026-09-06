import logging
import smtplib

from django.conf import settings
from django.core.mail import send_mail
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

logger = logging.getLogger(__name__)


class SMSAdapter:
    @staticmethod
    def _to_e164(phone: str) -> str:
        phone = phone.strip()
        if phone.startswith("+"):
            return phone
        country_code = getattr(settings, "PHONE_COUNTRY_CODE", "+1")
        if country_code == "+1":
            if phone.startswith("001"):
                return f"+{phone[2:]}"
            if phone.startswith("1") and len(phone) == 11:
                return f"+{phone}"
        if phone.startswith("0"):
            phone = phone[1:]
        if phone.startswith(country_code.lstrip("+")):
            return f"+{phone}"
        return f"{country_code}{phone}"

    @staticmethod
    def send_otp(phone_number: str, code: str) -> None:
        to_number = SMSAdapter._to_e164(phone_number)
        if getattr(settings, "OTP_MOCK_MODE", False):
            logger.info("[SMS MOCK] To: %s — Code: %s", to_number, code)
            return

        demo_phone = getattr(settings, "DEMO_PHONE_NUMBER", None)
        if demo_phone:
            to_clean = to_number.lstrip("+")
            demo_clean = demo_phone.lstrip("+")
            if to_number == demo_phone or to_clean == demo_clean or demo_clean.endswith(to_clean) or to_clean.endswith(demo_clean):
                logger.info("[DEMO] Skipping SMS for demo phone %s — Code: %s", to_number, code)
                return

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Your SPARK verification code: {code}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number,
            )
        except Exception as e:
            logger.warning(
                "Twilio send failed: %s — OTP for %s: %s",
                e,
                to_number,
                code,
            )


class EmailAdapter:
    @staticmethod
    def send_invite(email: str, password: str) -> None:
        try:
            send_mail(
                subject="[SPARK] Your Account Credentials",
                message=(
                    f"Your SPARK government account has been created.\n\n"
                    f"Email: {email}\n"
                    f"Password: {password}\n\n"
                    f"Please log in and change your password."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            logger.warning("Email send failed to %s: %s", email, e)

    @staticmethod
    def send_reset_code(email: str, code: str) -> None:
        if getattr(settings, "OTP_MOCK_MODE", False) or email in ("test@gmail.com",):
            logger.info("[EMAIL MOCK/DEMO] Skipping reset email to %s — Code: %s", email, code)
            return
        try:
            send_mail(
                subject="[SPARK] Password Reset Code",
                message=f"Your password reset code is: {code}\n\nThis code expires in 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            logger.warning("Email send failed to %s: %s", email, e)

    @staticmethod
    def send_otp(email: str, code: str) -> None:
        if getattr(settings, "OTP_MOCK_MODE", False) or email in ("test@gmail.com",):
            logger.info("[EMAIL MOCK/DEMO] Skipping OTP email to %s — Code: %s", email, code)
            return
        try:
            send_mail(
                subject="[SPARK] Your Verification Code",
                message=f"Your verification code is: {code}\n\nThis code expires in 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            logger.warning("Email send failed to %s: %s", email, e)
