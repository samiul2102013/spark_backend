from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client


class SMSAdapter:
    @staticmethod
    def send_otp(phone_number: str, code: str) -> None:
        if getattr(settings, "OTP_MOCK_MODE", False):
            print(f"[SMS MOCK] To: {phone_number} — Code: {code}")
            return
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"Your SPARK verification code: {code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number,
        )


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
