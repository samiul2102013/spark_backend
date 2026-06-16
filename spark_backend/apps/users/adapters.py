import logging

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
        if phone.startswith("00"):
            return f"+{phone[2:]}"
        if phone.startswith("0"):
            return f"+880{phone[1:]}"
        return f"+{phone}"

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
                "Twilio send failed (status=%s): %s — falling back to log",
                e.status,
                e.msg,
            )
            logger.info("[SMS FALLBACK] To: %s — Code: %s", to_number, code)


class EmailAdapter:
    @staticmethod
    def send_invite(email: str, invite_url: str) -> None:
        send_mail(
            subject="[SPARK] You're invited",
            message=f"Click the link to accept your invitation:\n{invite_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

    @staticmethod
    def send_reset_code(email: str, code: str) -> None:
        send_mail(
            subject="[SPARK] Password Reset Code",
            message=f"Your password reset code is: {code}\n\nThis code expires in 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
