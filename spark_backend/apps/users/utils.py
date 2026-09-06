import math
import random
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.hubs.models import Hub

from .adapters import SMSAdapter

User = get_user_model()


def resolve_user_by_phone(phone: str):
    """
    Find a user by phone number, accepting both E.164 (e.g. "+8801856669533", "+101521584710")
    and raw formats (e.g. "01856669533", "01521584710") in either direction.
    """
    stripped = phone.strip()
    normalized = SMSAdapter._to_e164(stripped)
    candidates = [normalized, stripped]

    demo_phone = getattr(settings, "DEMO_PHONE_NUMBER", None)
    if demo_phone:
        candidates.append(demo_phone)
        candidates.append(demo_phone.lstrip("+"))

    if stripped.startswith("+"):
        digits = stripped.lstrip("+")
        candidates.append(digits)
        country_digits = getattr(settings, "PHONE_COUNTRY_CODE", "+1").lstrip("+")
        if digits.startswith(country_digits):
            local = digits[len(country_digits):]
            candidates.append(local)
            if local.startswith("1") and not local.startswith("0"):
                candidates.append(f"0{local}")
    else:
        # Bare digits entered (e.g. 01521584710)
        candidates.append(f"+{stripped}")
        candidates.append(f"+1{stripped}")
        if stripped.startswith("0"):
            candidates.append(f"+1{stripped[1:]}")
        country_digits = getattr(settings, "PHONE_COUNTRY_CODE", "+1").lstrip("+")
        if country_digits != "1" and stripped.startswith("1") and len(stripped) == 11:
            candidates.append(f"+1{stripped}")

    for candidate in dict.fromkeys(candidates):
        try:
            return User.objects.get(phone_number=candidate)
        except User.DoesNotExist:
            continue
    return None


def generate_otp(phone: str) -> str:
    if getattr(settings, "OTP_MOCK_MODE", False):
        code = "000000"
        print(f"[OTP MOCK] Code for {phone}: {code}")
    else:
        code = f"{random.randint(100000, 999999)}"
    cache.set(f"otp:{phone}", code, timeout=300)
    return code


def verify_otp(phone: str, code: str) -> bool:
    demo_phone = getattr(settings, "DEMO_PHONE_NUMBER", None)
    demo_otp = getattr(settings, "DEMO_OTP_CODE", "000000")
    if demo_phone and code == demo_otp:
        phone_digits = phone.lstrip("+")
        demo_digits = demo_phone.lstrip("+")
        if (
            phone == demo_phone
            or phone_digits == demo_digits
            or demo_digits.endswith(phone_digits)
            or phone_digits.endswith(demo_digits)
            or (len(phone_digits) >= 10 and len(demo_digits) >= 10 and phone_digits[-10:] == demo_digits[-10:])
        ):
            return True

    if getattr(settings, "OTP_MOCK_MODE", False) and code == "000000":
        return True
    stored = cache.get(f"otp:{phone}")
    if stored is not None and stored == code:
        cache.delete(f"otp:{phone}")
        return True
    return False


def haversine(lat1, lng1, lat2, lng2) -> float:
    lat1, lng1, lat2, lng2 = float(lat1), float(lng1), float(lat2), float(lng2)
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def assign_hubs(lat: float, lng: float) -> Tuple[Optional[Hub], Optional[Hub]]:
    hubs = Hub.objects.filter(status="open")
    scored = sorted(
        [(haversine(lat, lng, float(h.latitude), float(h.longitude)), h) for h in hubs],
        key=lambda x: x[0],
    )
    primary = scored[0][1] if scored else None
    secondary = scored[1][1] if len(scored) > 1 else None
    return primary, secondary
