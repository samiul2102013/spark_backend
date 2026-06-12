# ChargeSafe Auth — Quick Reference

Base: `http://localhost/api/v1`

| # | Method | Path | Auth | Body |
|---|--------|------|------|------|
| 1 | POST | `/auth/register/` | — | `{"phone","full_name","household_size","medical_needs","latitude","longitude"}` |
| 2 | POST | `/auth/otp/send/` | — | `{"phone"}` |
| 3 | POST | `/auth/otp/verify/` | — | `{"phone","code"}` |
| 4 | POST | `/auth/login/` | — | `{"identifier","password"}` |
| 5 | POST | `/auth/refresh/` | — | `{"refresh"}` |
| 6 | POST | `/auth/biometric/register/` | JWT | `{"key"}` |
| 7 | POST | `/auth/biometric/login/` | — | `{"key"}` |
| 8 | POST | `/auth/offline-token/` | JWT | — |
| 9 | POST | `/auth/invite/{token}/` | — | — |
| 10 | POST | `/auth/invite/accept/` | — | `{"token","password","confirm_password"}` |
| 11 | POST | `/auth/forgot-password/` | — | `{"identifier"}` |
| 12 | POST | `/auth/reset-password/` | — | `{"identifier","code","new_password","confirm_password"}` |
| 13 | GET | `/users/profile/` | JWT | — |
| 14 | PUT | `/users/profile/` | JWT | `{"full_name"?,"email"?,"household_size"?,"medical_needs"?}` |
| 15 | PUT | `/users/change-password/` | JWT | `{"old_password","new_password","confirm_password"}` |
| 16 | PATCH | `/admin/users/{id}/set-role/` | Admin | `{"role":"coordinator"}` |
| 17 | POST | `/admin/users/invite/` | Admin | `{"email","full_name"}` |

## Quick smoke test (one-liners)

```powershell
# Some endpoints use file-based body because JWT tokens contain + which
# PowerShell curl.exe doesn't handle inline. Use the test-auth.ps1 script
# for a guided walkthrough, or pipe JSON files with @file.txt syntax.

# Health
curl.exe -s http://localhost/api/v1/health/

# Register
curl.exe -s -X POST http://localhost/api/v1/auth/register/ -H "Content-Type: application/json" -d "{"""phone""":"""+18765550001""","""full_name""":"""John""","""latitude""":17.97,"""longitude""":-76.79}"

# Login (admin)
curl.exe -s -X POST http://localhost/api/v1/auth/login/ -H "Content-Type: application/json" -d "{"""identifier""":"""admin@test.com""","""password""":"""admin1234"""}"
```
