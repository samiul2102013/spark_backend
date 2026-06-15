from django.conf import settings
from django.core.mail import send_mail


class SMSAdapter:
    @staticmethod
    def send_otp(phone_number: str, code: str) -> None:
        print(f"[SMS] To: {phone_number} — Your SPARK verification code: {code}")


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
