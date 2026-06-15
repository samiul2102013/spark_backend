# Mobile API Testing Guide

**✅ You're already logged in - Use your JWT token now!**

**Base URL**: `http://spark.kodevio.com:8000/api/v1/`
**Authorization**: `Bearer YOUR_JWT_TOKEN`

---

## Step 1: Dashboard & Map (Home Screen)
**What user sees after login**

### 1. Get Dashboard Overview
```
GET /api/v1/dashboard/overview/
Authorization: Bearer YOUR_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "total_hazards_active": 0,
    "my_bookings_upcoming": 0,
    "notifications_unread": 0,
    "hubs_nearby": []
  }
}
```

### 2. Get Map Data
```
GET /api/v1/dashboard/map/
Authorization: Bearer YOUR_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "hubs": [
      {
        "id": 1,
        "name": "Central Hub",
        "latitude": 23.8,
        "longitude": 90.4,
        "status": "active",
        "battery_percentage": 85
      }
    ],
    "hazards": [
      {
        "id": 1,
        "category": "flood",
        "latitude": 23.810,
        "longitude": 90.410,
        "severity": "low"
      }
    ]
  }
}
```

---

## Step 2: Check Notifications
**Push notifications badge**

### 3. Get Unread Notifications
```
GET /api/v1/notifications/?unread_only=true
Authorization: Bearer YOUR_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "type": "broadcast",
      "title": "Meeting Update",
      "body": "Hub meeting moved to 2 PM",
      "read": false,
      "hub": 1
    }
  ]
}
```

### 4. Get All Notifications
```
GET /api/v1/notifications/?unread_only=false
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Step 3: View Open Hubs
**Find where to go for safety**

### 5. Get Open Hubs
```
GET /api/v1/hubs/?status=registered
Authorization: Bearer YOUR_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Dhaka Central Hub",
      "address": "Gulshan-1, Road 5",
      "latitude": 23.732,
      "longitude": 90.418,
      "status": "active",
      "battery_percentage": 92
    }
  ]
}
```

### 6. Get All Hubs
```
GET /api/v1/hubs/
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Step 4: Report a Hazard
**Mobile screen for reporting emergencies**

### 7. Create Hazard Report
```
POST /api/v1/hazards/create/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "category": "flood",
  "description": "Water level rising, roads blocked",
  "latitude": 23.820,
  "longitude": 90.420,
  "hub": 1,
  "client_uuid": "MOBILE-REQ-001"
}
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "category": "flood",
    "description": "Water level rising, roads blocked",
    "latitude": 23.820,
    "longitude": 90.420,
    "severity": "medium",
    "status": "active",
    "reporter": "phone_number"
  }
}
```

### 8. View Active Hazards
```
GET /api/v1/hazards/?status=active
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Step 5: Make a Booking
**Plan your visit to a hub**

### 9. Get My Bookings
```
GET /api/v1/bookings/?status=pending&status=upcoming
Authorization: Bearer YOUR_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": []
}
```

### 10. Create Booking
```
POST /api/v1/bookings/create/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "hub": 1,
  "start_time": "2026-06-16T10:00:00Z",
  "end_time": "2026-06-16T12:00:00Z",
  "client_uuid": "MOBILE-REQ-002"
}
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "hub": 1,
    "start_time": "2026-06-16T10:00:00Z",
    "end_time": "2026-06-16T12:00:00Z",
    "status": "pending",
    "people_count": 1
  }
}
```

### 11. Confirm Booking Details
```
GET /api/v1/bookings/1/
Authorization: Bearer YOUR_JWT_TOKEN
```

### 12. Cancel Booking
```
PATCH /api/v1/bookings/1/cancel/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "client_uuid": "MOBILE-REQ-003"
}
```

---

## Step 6: Submit Check-in
**Arrive at hub**

### 13. Submit Check-in
```
POST /api/v1/checkins/create/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "hub": 1,
  "people_count": 2,
  "status": "safe",
  "road_access": "open",
  "latitude": 23.825,
  "longitude": 90.425,
  "client_uuid": "MOBILE-REQ-004"
}
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "hub": 1,
    "people_count": 2,
    "status": "safe",
    "road_access": "open",
    "timestamp": "2026-06-16T10:30:00Z"
  }
}
```

### 14. View My Check-in History
```
GET /api/v1/checkins/?hub=1
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Step 7: View Booking History
**Past check-ins and bookings**

### 15. Get Complete Bookings
```
GET /api/v1/bookings/?status=completed
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Step 8: Broadcast to Hubs
**Send alerts/notifications**

### 16. Create Broadcast
```
POST /api/v1/broadcasts/create/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "hub": 1,
  "subject": "Safety Update",
  "body": "Power is restored. Please come soon.",
  "priority": "info"
}
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "hub": 1,
    "subject": "Safety Update",
    "body": "Power is restored. Please come soon.",
    "priority": "info",
    "created_at": "2026-06-16T10:00:00Z"
  }
}
```

---

## Step 9: Update Profile (Optional)

### 17. Update Profile
```
PUT /api/v1/users/profile/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "full_name": "Test User Updated",
  "household_size": 4,
  "medical_needs": "diabetes"
}
```

---

## Testing Checklist

Use this checklist to test the complete mobile workflow:

- [ ] **Dashboard** — Get overview & map
- [ ] **Notifications** — View unread & read notifications
- [ ] **Hubs** — View available hubs
- [ ] **HazardReporting** — Create hazard report
- [ ] **HazardsList** — View active hazards
- [ ] **Bookings** — Create booking
- [ ] **BookingsList** — View my bookings
- [ ] **CancelBooking** — Cancel booking
- [ ] **CheckIn** — Submit check-in
- [ ] **CheckHistory** — View check-in history
- [ ] **Broadcast** — Create broadcast
- [ ] **Profile** — Update user info

---

## Token Management

Since access tokens expire quickly:
- **Access Token**: Valid for ~5 minutes
- **Refresh Token**: Get new access token before they expire

### Get New Token (if needed):
```
POST /api/v1/auth/refresh/
Authorization: Bearer YOUR_REFRESH_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "refresh": "your_refresh_token_value"
}
```

---

## Common Error Codes

| Code | Meaning | How to Fix |
|------|---------|------------|
| 401 | Unauthorized | Get new token, ensure Bearer format |
| 400 | Bad Request | Check request body format |
| 403 | Forbidden | Check user permissions |
| 404 | Not Found | Verify endpoint path |
| 500 | Server Error | Contact support |

---

## Complete Workflow

1. **Login** ✅ Done
2. **View Dashboard** → Check location, status ✅
3. **Get Notifications** → See alerts ✅
4. **View Hub** → Choose any hub ✅
5. **Report Hazard** → Emergency report ✅
6. **Make Booking** → Plan visit ✅
7. **Submit Check-in** → Arrived at hub ✅
8. **View History** → Past activities ✅
9. **Broadcast** → Send messages ✅
10. **Update Profile** → Keep info current ✅