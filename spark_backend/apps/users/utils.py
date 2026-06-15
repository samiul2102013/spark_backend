import math
import random
from typing import Optional, Tuple

from django.conf import settings
from django.core.cache import cache

from apps.hubs.models import Hub


def generate_otp(phone: str) -> str:
    if getattr(settings, "OTP_MOCK_MODE", False):
        code = "000000"
        print(f"[OTP MOCK] Code for {phone}: {code}")
    else:
        code = f"{random.randint(100000, 999999)}"
    cache.set(f"otp:{phone}", code, timeout=300)
    return code


def verify_otp(phone: str, code: str) -> bool:
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
