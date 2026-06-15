# API Testing Guide — Authentication Setup

## When to Use Authorization Header

### ❌ DO NOT USE for Phase 1

**Endpoints**: `/auth/register/`, `/auth/otp/send/`, `/auth/otp/verify/`, `/auth/login/`

**Authorization Type**: `None` (or leave empty)

```json
{
  "phone": "01712345678",
  "full_name": "Test User",
  "household_size": 4,
  "medical_needs": "none",
  "latitude": 23.8,
  "longitude": 90.4
}
```

---

### ✅ USE for Phase 2-5

**Endpoints**: All after successful login

**Authorization Type**: `Bearer Token`

**Token**: `{{access}}` (the access_token from login response)

---

## Step-by-Step Guide

### Phase 1: Setup Authentication (No Token Needed)

1. **Register**
   - URL: `/api/v1/auth/register/`
   - Auth: **None**
   - Body: phone, full_name, household_size, medical_needs, latitude, longitude

2. **Send OTP**
   - URL: `/api/v1/auth/otp/send/`
   - Auth: **None**
   - Body: `{"phone": "01712345678"}`

3. **Verify OTP**
   - URL: `/api/v1/auth/otp/verify/`
   - Auth: **None**
   - Body: `{"phone": "01712345678", "code": "123456"}`

4. **Login**
   - URL: `/api/v1/auth/login/`
   - Auth: **None**
   - Body: `{"username": "01712345678", "password": "your_password"}`
   - **Save the access_token** from response

### Phase 2: Set Bearer Token

After login, you'll get JSON response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Now set this in your collection or for all Phase 2-5 endpoints:

```
Authorization Type: Bearer Token
Token: {{access}}
```

---

## Apidog UI Instructions

### Option 1: Collection Global Variable (Recommended)

1. Click **Collection Settings** (gear icon)
2. Add variable: `access` (or `bearerToken`) with value: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`
3. Next to each endpoint in Phase 2-5:
   - Click **Authorization** section
   - Type: `Bearer Token`
   - Token: `{{access}}`

### Option 2: Per-Endpoint Authorization

1. Open any Phase 2 endpoint (e.g., `GET /api/v1/hubs/`)
2. Click **Authorization** section
3. Type: `Bearer Token`
4. Token: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`
5. Apply to all Phase 2-5 endpoints

---

## Quick Test Workflow

```bash
# Phase 1: Register
curl -X POST http://spark.kodevio.com:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "01712345678",
    "full_name": "Test User",
    "household_size": 4,
    "medical_needs": "none",
    "latitude": 23.8,
    "longitude": 90.4
  }'

# Phase 1: Login (get token)
curl -X POST http://spark.kodevio.com:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "01712345678",
    "password": "manual123"
  }'

# Save the "access" value from login response

# Phase 2-5: Use Bearer Token
curl -X GET http://spark.kodevio.com:8000/api/v1/hubs/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

## Pro Tips

1. **Never use JWT Schema** type unless your API specifically defines a custom security scheme
2. **Bearer Token** is the standard JWT authentication method
3. **Access tokens expire** after 5 minutes — use refresh token if needed
4. **Test Phase 1 first** without any Authorization header
5. **Copy the access_token** from login response exactly as-is