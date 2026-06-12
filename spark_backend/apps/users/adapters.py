class SMSAdapter:
    @staticmethod
    def send_otp(phone_number: str, code: str) -> None:
        print(f"[SMS] To: {phone_number} — Your SPARK verification code: {code}")


class EmailAdapter:
    @staticmethod
    def send_invite(email: str, invite_url: str) -> None:
        print(f"[EMAIL] To: {email} — SPARK invite link: {invite_url}")

    @staticmethod
    def send_reset_code(email: str, code: str) -> None:
        print(f"[EMAIL] To: {email} — SPARK password reset code: {code}")
