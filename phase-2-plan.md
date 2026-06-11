# Phase 2 — Authentication & User APIs

## Goal
Implement the complete auth system for all three products (Mobile App, Web Dashboard, Admin Panel) plus the user profile and registration flows. Every endpoint follows the strict View→Serializer→Service pattern.

## What we will build

### 1. Third-Party Packages
Add to `requirements.txt`:
- `djangorestframework-simplejwt` — already present, configure properly
- `drf-spectacular` — already present (Swagger docs for all new endpoints)

### 2. Auth App (`apps/users/`) — Implementation

#### Models (already exist — no changes)
- `User` — phone PK, role, hub FK, household_size, medical_needs, community_secret_code
- Need to add: `email` field as unique for admin/gov accounts, `biometric_key` for biometric login

#### Serializers (NEW)
| Serializer | Purpose |
|------------|---------|
| `PhoneLoginSerializer` | Validate phone number |
| `OTPVerifySerializer` | Validate OTP + phone |
| `EmailLoginSerializer` | Validate email + password |
| `RegisterSerializer` | Validate name, phone, community code, household size, medical needs |
| `ForgotPasswordSerializer` | Validate email |
| `ResetPasswordSerializer` | Validate OTP + new password |
| `ProfileSerializer` | Read/write user profile |
| `BiometricRegisterSerializer` | Store biometric key |
| `OfflineTokenSerializer` | Generate pre-saved OTP for offline |

#### Services (NEW)
| Service Method | Logic |
|----------------|-------|
| `AuthService.send_otp(phone)` | Generate 6-digit OTP, store in cache (5min TTL), send via adapter (Twilio placeholder) |
| `AuthService.verify_otp(phone, code)` | Check cache, return JWT pair on success |
| `AuthService.register(data)` | Validate secret code → auto-assign hub → create user → return JWT |
| `AuthService.forgot_password(email)` | Send reset OTP to email |
| `AuthService.reset_password(data)` | Verify OTP → update password |
| `AuthService.generate_offline_token(user)` | Pre-compute short-lived token for offline use |

#### Views/ViewSets (NEW)
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/auth/otp/send/` | POST | None | Send OTP to phone |
| `/api/v1/auth/otp/verify/` | POST | None | Verify OTP → return JWT |
| `/api/v1/auth/login/` | POST | None | Email + password login → JWT |
| `/api/v1/auth/register/` | POST | None | Resident onboarding |
| `/api/v1/auth/forgot-password/` | POST | None | Send reset code |
| `/api/v1/auth/reset-password/` | POST | None | Reset with OTP |
| `/api/v1/auth/biometric/register/` | POST | JWT | Store biometric key |
| `/api/v1/auth/biometric/login/` | POST | None | Biometric → JWT |
| `/api/v1/auth/offline-token/` | POST | JWT | Generate offline token |
| `/api/v1/auth/refresh/` | POST | None | Refresh JWT |
| `/api/v1/users/profile/` | GET/PUT | JWT | Read/update profile |
| `/api/v1/users/change-password/` | PUT | JWT | Change password |
| `/api/v1/users/security/` | GET | JWT | Security settings |

### 3. JWT Configuration
- Access token: 30 min (mobile) / 2 hours (dashboard)
- Refresh token: 7 days
- Custom claims: `role`, `hub_id`, `phone_number`
- Blacklist on logout (optional, Phase 3)

### 4. OTP Flow
```
POST /api/v1/auth/otp/send/  →  {"phone": "+18765551234"}
  → Cache OTP (key: `otp_{phone}`, value: `123456`, TTL: 300s)
  → Adapter.send_sms(phone, "Your SPARK code: 123456")
  → {"status": "success", "message": "OTP sent"}

POST /api/v1/auth/otp/verify/  →  {"phone": "+18765551234", "code": "123456"}
  → Check cache → if match → create/return user → JWT pair
  → {"status": "success", "data": {"access": "...", "refresh": "...", "user": {...}}}
```

### 5. Registration Flow
```
POST /api/v1/auth/register/
  {"full_name": "John", "phone_number": "+1876...", "community_secret_code": "ABC123",
   "household_size": 4, "medical_needs": ""}
  → Service.register(validated_data)
    → Lookup Hub by community_secret_code
    → Auto-assign user to hub
    → Create user (role=resident)
    → Return JWT
```

### 6. Permissions (update core/permissions.py)
| Permission | Logic |
|------------|-------|
| `IsResident` | `user.role == "resident"` |
| `IsCoordinator` | `user.role == "coordinator"` |
| `IsAdmin` | `user.role == "admin"` |
| `IsGovernment` | `user.role == "government"` |
| `IsCoordinatorOrReadOnly` | GET allowed for all, write needs coordinator+ |

### 7. URL Structure
```
config/urls.py
├── api/v1/health/
├── api/v1/schema/
├── api/v1/docs/
├── api/v1/auth/       ← apps/users/urls.py (auth namespace)
└── api/v1/users/      ← apps/users/urls.py (profile namespace)
```

### 8. Mobile App Auth Screens Map

| Figma Screen | Endpoint(s) | Phase |
|-------------|-------------|-------|
| Splash 1 | — (client-only) | — |
| Onboarding 4/5/6 | `POST /auth/register/` | Phase 2 |
| Sign in | `POST /auth/otp/send/` + `POST /auth/otp/verify/` | Phase 2 |
| Biometric | `POST /auth/biometric/register/` + `POST /auth/biometric/login/` | Phase 2 |
| Offline login pre-saved OTP | `POST /auth/offline-token/` | Phase 2 |
| Forgot Pass | `POST /auth/forgot-password/` | Phase 2 |
| Create New Pass | `POST /auth/reset-password/` | Phase 2 |
| Profile | `GET/PUT /users/profile/` | Phase 2 |
| Personal Information | `GET/PUT /users/profile/` | Phase 2 |
| Change Pass | `PUT /users/change-password/` | Phase 2 |
| Security | `GET /users/security/` | Phase 2 |

### 9. Admin/Web Dashboard Auth Screens Map

| Figma Screen | Endpoint(s) | Phase |
|-------------|-------------|-------|
| Log in | `POST /auth/login/` | Phase 2 |
| Forgot Password | `POST /auth/forgot-password/` | Phase 2 |
| Verify Email | `POST /auth/reset-password/` (OTP step) | Phase 2 |
| Two-Step Verification | `POST /auth/otp/verify/` | Phase 2 |
| Create New Password | `POST /auth/reset-password/` | Phase 2 |

### 10. Adapters (stubs — real integration in Phase 3)
- `SMSAdapter.send_otp(phone, code)` — prints to console / Celery task placeholder
- `EmailAdapter.send_reset_link(email, code)` — console backend

### 11. Tests
- `apps/users/tests/test_auth.py` — OTP flow, login, registration, edge cases
- `apps/users/tests/test_serializers.py` — validation logic
- Run: `docker compose exec django python -m pytest apps/users/ -v`

---

## What we will NOT build (Phase 2)
- WhatsApp/SMS real integration (Phase 3 — just console stubs)
- Bluetti adapter (Phase 5)
- Hazard/Check-in/Booking endpoints (Phase 3+)
- Admin-specific endpoints (Phase 4+)
- Offline sync conflict resolution (Phase 5+)

## Deliverables
- 12 new endpoints fully functional via Swagger UI
- OTP flow with Redis cache (verify via Swagger)
- JWT auth working for all three roles
- `POST /auth/register/` with hub auto-assignment
- All tests passing

## CI/CD Note
The current `deploy.yml` calls `docker compose pull` which will fail since we don't push to a registry. Fix: change to `docker compose up -d --build --remove-orphans` only (no pull). This needs a small edit to the workflow.

---

Files to modify:
- `requirements.txt` — add `django-redis` for OTP cache
- `config/settings/base.py` — add SIMPLE_JWT config, OTP cache settings
- `config/urls.py` — add auth + users routes
- `core/permissions.py` — already done (verify)
- `apps/users/models.py` — add `email` uniqueness, `biometric_key`
- `apps/users/serializers.py` — rewrite with 8 serializers
- `apps/users/services.py` — NEW: AuthService
- `apps/users/views.py` — NEW: AuthViewSet, ProfileViewSet
- `apps/users/urls.py` — NEW: route definitions
- `apps/users/adapters.py` — NEW: SMSAdapter, EmailAdapter stubs
- `apps/users/tests/` — NEW: test files
- `.github/workflows/deploy.yml` — remove `docker compose pull`
