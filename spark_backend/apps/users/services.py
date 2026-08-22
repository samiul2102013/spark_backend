import secrets
import uuid
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import SparkBaseError

from .adapters import EmailAdapter, SMSAdapter
from .authentication import authenticate
from .utils import assign_hubs, generate_otp, verify_otp

User = get_user_model()


class AuthError(SparkBaseError):
    status_code = 400
    default_detail = "Authentication failed."
    default_code = "auth_error"


class AuthService:

    # ── Resident OTP Flow ──────────────────────────────────────────

    @transaction.atomic
    def register(
        self,
        phone: str,
        full_name: str,
        latitude: float,
        longitude: float,
        household_size: Optional[int] = None,
        medical_needs: str = "",
    ) -> dict:
        phone = SMSAdapter._to_e164(phone)
        if User.objects.filter(phone_number=phone).exists():
            raise AuthError("Phone number already registered.")

        primary_hub, secondary_hub = assign_hubs(latitude, longitude)

        user = User.objects.create_user(
            phone_number=phone,
            full_name=full_name,
            role="resident",
            household_size=household_size,
            medical_needs=medical_needs,
            hub=primary_hub,
            secondary_hub=secondary_hub,
            latitude=latitude,
            longitude=longitude,
            is_active=False,
        )
        code = generate_otp(phone)
        SMSAdapter.send_otp(phone, code)
        return {"user_id": user.phone_number}

    def send_otp(self, phone: str) -> dict:
        phone = SMSAdapter._to_e164(phone)
        try:
            User.objects.get(phone_number=phone, role__in=("resident", "coordinator"))
        except User.DoesNotExist:
            raise AuthError("No active resident or coordinator found with this number.")
        code = generate_otp(phone)
        SMSAdapter.send_otp(phone, code)
        return {"message": "OTP sent"}

    def verify_otp(self, phone: str, code: str) -> dict:
        phone = SMSAdapter._to_e164(phone)
        if not verify_otp(phone, code):
            raise AuthError("Invalid or expired OTP.")
        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            raise AuthError("User not found.")
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        return _jwt_response(user)

    # ── Email/Password Login ───────────────────────────────────────

    def login(self, username: str, password: str) -> dict:
        user = authenticate(username, password)
        if user is None:
            raise AuthError("Invalid credentials.")
        if not user.is_active:
            raise AuthError("Account is not active.")
        return _jwt_response(user)

    # ── Biometric ──────────────────────────────────────────────────

    def register_biometric(self, user: User, key: str) -> dict:
        user.biometric_key = key
        user.save(update_fields=["biometric_key"])
        return {"message": "Biometric key registered."}

    def biometric_login(self, key: str) -> dict:
        try:
            user = User.objects.get(biometric_key=key, is_active=True)
        except User.DoesNotExist:
            raise AuthError("Invalid biometric key.")
        return _jwt_response(user)

    # ── Apple Sign-In ──────────────────────────────────────────────

    def apple_login(self, identity_token: str, full_name: str = "") -> dict:
        from .apple_auth import AppleTokenVerifier

        verifier = AppleTokenVerifier()
        claims = verifier.verify(identity_token)

        sub = claims["sub"]
        email = claims.get("email")

        try:
            user = User.objects.get(apple_user_id=sub)
            return _jwt_response(user)
        except User.DoesNotExist:
            pass

        # Do NOT auto-link by email — that would let anyone with knowledge of
        # your email claim an Apple-linked account. A separate account is created.
        phone_number = f"apple-{uuid.uuid4().hex[:12]}"
        user = User.objects.create_user(
            phone_number=phone_number,
            full_name=full_name or "Apple User",
            apple_user_id=sub,
            email=email,
            role="resident",
            is_active=True,
        )
        return _jwt_response(user)

    # ── Offline Token ──────────────────────────────────────────────

    def issue_offline_token(self, user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        refresh.set_exp(lifetime=__import__("datetime").timedelta(hours=24))
        return {"offline_token": str(refresh.access_token)}

    # ── Government Invite ──────────────────────────────────────────

    def _generate_password(self) -> str:
        return secrets.token_urlsafe(12)

    def invite_government(self, email: str, full_name: str) -> dict:
        if User.objects.filter(email=email).exists():
            raise AuthError("Email already registered.")

        password = self._generate_password()

        user = User.objects.create_user(
            full_name=full_name,
            email=email,
            role="government",
            is_active=True,
            is_invite_accepted=True,
        )
        user.set_password(password)
        user.save(update_fields=["password"])

        EmailAdapter.send_invite(email, password)
        return {"message": "Invitation sent.", "email": email}

    def validate_invite(self, token: str) -> dict:
        user_pk = cache.get(f"invite:{token}")
        if not user_pk:
            raise AuthError("Invalid or expired invitation token.")
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            raise AuthError("User not found.")
        return {"email": user.email, "full_name": user.full_name}

    def accept_invite(self, token: str, password: str) -> dict:
        user_pk = cache.get(f"invite:{token}")
        if not user_pk:
            raise AuthError("Invalid or expired invitation token.")
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            raise AuthError("User not found.")
        user.set_password(password)
        user.is_invite_accepted = True
        user.save(update_fields=["password", "is_invite_accepted"])
        cache.delete(f"invite:{token}")
        return _jwt_response(user)

    # ── Password Reset ─────────────────────────────────────────────

    def forgot_password(self, identifier: str) -> dict:
        try:
            if "@" in identifier:
                user = User.objects.get(email=identifier)
            else:
                identifier = SMSAdapter._to_e164(identifier)
                user = User.objects.get(phone_number=identifier)
        except User.DoesNotExist:
            raise AuthError("User not found.")

        code = generate_otp(identifier)
        if user.email:
            EmailAdapter.send_reset_code(user.email, code)
        else:
            SMSAdapter.send_otp(user.phone_number, code)
        return {"message": "Reset code sent."}

    def verify_reset_otp(self, identifier: str, code: str) -> dict:
        if "@" not in identifier:
            identifier = SMSAdapter._to_e164(identifier)
        if not verify_otp(identifier, code):
            raise AuthError("Invalid or expired code.")
        try:
            if "@" in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(phone_number=identifier)
        except User.DoesNotExist:
            raise AuthError("User not found.")
        return {
            "message": "OTP verified.",
            "access": str(RefreshToken.for_user(user).access_token),
        }

    def reset_password(self, user: User, new_password: str) -> dict:
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return {"message": "Password reset successfully."}

    # ── Profile ────────────────────────────────────────────────────

    def update_profile(self, user: User, data: dict) -> User:
        allowed = ["full_name", "email", "household_size", "medical_needs", "profile_photo"]
        for field in allowed:
            if field in data:
                setattr(user, field, data[field])
        user.save()
        return user

    def set_password(self, user: User, new_password: str) -> dict:
        if user.has_usable_password():
            raise AuthError("You already have a password. Use change password instead.")
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return {"message": "Password set successfully."}

    def change_password(self, user: User, old_password: str, new_password: str) -> dict:
        if not user.has_usable_password():
            raise AuthError("You don't have a password. Use set password first.")
        if not user.check_password(old_password):
            raise AuthError("Your given old password is incorrect.")
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return {"message": "Password changed."}

    # ── Admin ──────────────────────────────────────────────────────

    def list_users(self, role=None, search=None):
        qs = User.objects.all()
        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone_number__icontains=search)
            )
        return qs

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @transaction.atomic
    def update_user(self, user_id, data):
        user = User.objects.get(id=user_id)
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        return user

    @transaction.atomic
    def delete_user(self, user_id):
        user = User.objects.get(id=user_id)
        user.delete()

    def delete_my_account(self, user):
        user.delete()

    def set_role(self, user: User, role: str) -> dict:
        if role not in ("resident", "coordinator", "government", "admin"):
            raise AuthError("Invalid role.")
        user.role = role
        user.save(update_fields=["role"])
        return {"message": f"Role updated to {role}."}


def _jwt_response(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "role": user.role,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "hub_id": user.hub_id,
            "secondary_hub_id": user.secondary_hub_id,
        },
    }
