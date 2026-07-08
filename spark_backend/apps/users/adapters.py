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
        phone = phone.strip().lstrip("+")
        if phone.startswith("1") and len(phone) == 11:
            return f"+{phone}"
        if phone.startswith("001"):
            return f"+{phone[2:]}"
        if phone.startswith("0"):
            phone = phone[1:]
        return f"+1{phone}"

    @staticmethod
    def send_otp(phone_number: str, code: str) -> None:
        to_number = SMSAdapter._to_e164(phone_number)
        if getattr(settings, "OTP_MOCK_MODE", False):
            logger.info("[SMS MOCK] To: %s — Code: %s", to_number, code)
            return
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Your SPARK verification code: {code}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number,
            )
        except TwilioRestException as e:
            logger.warning(
                "Twilio send failed (status=%s): %s — OTP for %s: %s",
                e.status,
                e.msg,
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
        except smtplib.SMTPException as e:
            logger.warning("Email send failed to %s: %s", email, e)

    @staticmethod
    def send_reset_code(email: str, code: str) -> None:
        try:
            send_mail(
                subject="[SPARK] Password Reset Code",
                message=f"Your password reset code is: {code}\n\nThis code expires in 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except smtplib.SMTPException as e:
            logger.warning("Email send failed to %s: %s", email, e)

    @staticmethod
    def send_otp(email: str, code: str) -> None:
        try:
            send_mail(
                subject="[SPARK] Your Verification Code",
                message=f"Your verification code is: {code}\n\nThis code expires in 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except smtplib.SMTPException as e:
            logger.warning("Email send failed to %s: %s", email, e)
