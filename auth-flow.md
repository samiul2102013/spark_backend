# ChargeSafe — Auth Flow Design

## Overview

Four user roles, two authentication methods, one unified system.

```
Role         Auth Method          Entry Point
──────────────────────────────────────────────────────
Resident  →  Phone + OTP          Mobile App (self-register)
Coordinator → Phone + OTP          Same as resident (promoted by admin)
Government → Email + Password      Web Dashboard (invited by admin)
Admin     →  Email + Password      Admin Panel (created via CLI/seed)
```

---

## Flow 1: Resident — Self-Registration (Mobile App)

```
Mobile App                            Server
──────────────────────────────────────────────────────
User fills form:
  full_name, phone,
  household_size,
  medical_needs
       │
       ▼
Gets lat/lng from
device GPS
       │
       ▼
POST /auth/register/  ──────────────►  Creates user (inactive)
{                                       Finds nearest hub via
  phone,                                haversine distance
  full_name,                            Assigns primary_hub
  household_size,                       Finds second-nearest hub
  medical_needs,                        Assigns secondary_hub
  latitude,                             role=resident
  longitude                             Sends OTP via SMS
}                                       │
                                        ▼
                              Response: { user_id, message: "OTP sent" }
       │
       ▼
User receives OTP
       │
       ▼
POST /auth/otp/verify/  ──────────────►  Verifies OTP
{                                       Sets user.is_active = true
  phone,                                Issues JWT
  code                                  │
}                                       ▼
                              Response: { access, refresh, user }

Subsequent logins:
1. POST /auth/otp/send/   → { phone }
2. POST /auth/otp/verify/ → { phone, code } → { access, refresh, user }
```

### Hub auto-assignment logic (server-side)

```
def assign_hubs(lat, lng):
    hubs = Hub.objects.filter(is_active=True)
    with_distances = []
    for hub in hubs:
        dist = haversine(lat, lng, hub.latitude, hub.longitude)
        with_distances.append((dist, hub))
    with_distances.sort(key=lambda x: x[0])
    primary   = with_distances[0][1] if len(with_distances) > 0 else None
    secondary = with_distances[1][1] if len(with_distances) > 1 else None
    return primary, secondary
```

### Validation rules
- Phone must be unique (not already registered)
- Latitude/Longitude required and validated range
- OTP stored in Redis with 5min TTL, 6 digits
- If no hubs exist within a reasonable radius, registration still succeeds (hub stays null)

---

## Flow 2: Government/NGO — Invitation & Login (Web Dashboard)

```
Admin Panel                  Government User              API
─────────────────────────────────────────────────────────────────
Admin creates
gov account
with email + name
       │
       ▼
POST /admin/users/invite/
       │
       ▼
System generates
one-time token
(expires 48h)
       │
       ▼
Sends email:
"Click to activate
your SPARK account"
       │
       ───────────────►  User clicks link
                         ────────────────►  GET /auth/invite/{token}/
                                              │
                                              ▼
                                          Shows: set password form
                                              │
                                              ▼
                         POST /auth/invite/accept/
                         { token, password, confirm_password }
                                              │
                                              ▼
                                          Account activated
                                          role: government
                                              │
                                              ▼
                         POST /auth/login/
                         { email, password }
                                              │
                                              ▼
                                          JWT issued
                                          { role: "government", ... }
```

### Validation rules
- Token is a signed JWT stored in Redis (48h TTL)
- Email must be unique across all users
- Government users have no phone_number (field left null)

---

## Flow 3: Coordinator — Promoted by Admin

```
Admin Panel
       │
       ▼
Admin navigates to
Management → Users
       │
       ▼
Searches/finds resident
       │
       ▼
PATCH /admin/users/{phone}/set-role/
{ role: "coordinator" }
       │
       ▼
User's role updated
       │
       ▼
Coordinator now logs in
SAME as resident flow
(phone + OTP)
       │
       ▼
JWT now contains
{ role: "coordinator", hub_id, secondary_hub_id, permissions: [...] }
```

- Coordinator inherits all resident capabilities
- Additional: can update hub status, broadcast messages, view check-ins
- No separate registration flow needed

---

## Flow 4: Admin — Direct Creation

```
Server setup:
python manage.py createsuperuser
→ email (required)
→ full_name
→ password

OR via seed script / admin panel.

Login:
POST /auth/login/  →  { identifier, password }
                    →  { access, refresh, user: { role: "admin", ... } }
```

---

## Unified Login Endpoint (for gov/admin)

```
POST /auth/login/
Request: { identifier: "user@example.com" | "+18765551234", password: "..." }

Logic:
  if identifier looks like email → auth by email
  if identifier looks like phone → auth by phone
  else → 400 "Invalid identifier"

Response:
{
  "status": "success",
  "data": {
    "access": "eyJ...",
    "refresh": "eyJ...",
    "user": {
      "role": "resident" | "coordinator" | "government" | "admin",
      "full_name": "...",
      "phone_number": "..." | null,
      "email": "..." | null,
      "hub_id": 1 | null,
      "secondary_hub_id": 2 | null
    }
  }
}
```

---

## Endpoint Summary

| # | Method | Endpoint | Auth | Role | Purpose |
|---|--------|----------|------|------|---------|
| 1 | POST | `/auth/register/` | None | — | Resident onboarding with lat/lng hub assignment |
| 2 | POST | `/auth/otp/send/` | None | — | Send OTP to phone for verification |
| 3 | POST | `/auth/otp/verify/` | None | — | Verify OTP → JWT |
| 4 | POST | `/auth/login/` | None | — | Email/Phone + password |
| 5 | POST | `/auth/refresh/` | None | — | Refresh JWT |
| 6 | POST | `/auth/biometric/register/` | JWT | Resident | Store biometric key |
| 7 | POST | `/auth/biometric/login/` | None | — | Biometric → JWT |
| 8 | POST | `/auth/offline-token/` | JWT | Resident | Pre-saved offline OTP |
| 9 | GET | `/auth/invite/{token}/` | None | — | Validate invite token |
| 10 | POST | `/auth/invite/accept/` | None | — | Accept invite, set password |
| 11 | POST | `/auth/forgot-password/` | None | — | Send reset code |
| 12 | POST | `/auth/reset-password/` | None | — | Reset with code |
| 13 | GET | `/users/profile/` | JWT | Any | Read profile |
| 14 | PUT | `/users/profile/` | JWT | Any | Update profile |
| 15 | PUT | `/users/change-password/` | JWT | Any | Change password |
| 16 | PATCH | `/admin/users/{id}/set-role/` | JWT | Admin | Promote to coordinator |
| 17 | POST | `/admin/users/invite/` | JWT | Admin | Invite government user |

---

## JWT Payload Structure

```json
{
  "sub": "+18765551234" | "user@example.com",
  "sub_type": "phone" | "email",
  "role": "resident" | "coordinator" | "government" | "admin",
  "hub_id": 1 | null,
  "secondary_hub_id": 2 | null,
  "exp": 1718000000,
  "iat": 1717998200
}
```

- Access token TTL: **30 min** (mobile), **2 hours** (dashboard)
- Refresh token TTL: **7 days**

---

## User Model — Updated Fields

| Field | Type | Notes |
|-------|------|-------|
| `phone_number` | PK, CharField | Residents only, null for gov-only users |
| `email` | Unique, nullable | Required for admin/gov, optional for residents |
| `full_name` | CharField | Always required |
| `role` | ChoiceField | resident / coordinator / government / admin |
| `hub` | FK → Hub | Auto-assigned by lat/lng, null for gov |
| `secondary_hub` | FK → Hub | Second-nearest hub, null if none nearby |
| `latitude` | Decimal(9,6), nullable | Captured from device GPS |
| `longitude` | Decimal(9,6), nullable | Captured from device GPS |
| `biometric_key` | CharField, nullable | For biometric login |
| `household_size` | Integer, nullable | Residents only |
| `medical_needs` | TextField | Residents only |
| `is_active` | Boolean | False until OTP verified |
| `is_invite_accepted` | Boolean | False until gov user activates |

## Hub Model — New Fields Required

| Field | Type | Notes |
|-------|------|-------|
| `latitude` | Decimal(9,6) | Center of hub location |
| `longitude` | Decimal(9,6) | Center of hub location |
