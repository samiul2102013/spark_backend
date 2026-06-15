# Government Dashboard API Testing Guide

**Government Officials Dashboard**

**Base URL**: `http://spark.kodevio.com:8000/api/v1/`

**Authentication**: Government admin role (different JWT token)

---

## Step 1: Get Government Dashboard Overview
**Main government dashboard screen**

### 1. View All Reports
```
GET /api/v1/dashboard/reports/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "total_residents_safe": 15,
    "total_hazards_active": 3,
    "total_hubs_operational": 5,
    "alerts_sent": 8
  }
}
```

### 2. Get All Hazards Map Data
```
GET /api/v1/dashboard/map/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "hubs": [],
    "hazards": [
      {
        "id": 1,
        "category": "flood",
        "description": "Flash flooding in north district",
        "latitude": 23.780,
        "longitude": 90.380,
        "severity": "high",
        "status": "active"
      }
    ]
  }
}
```

---

## Step 2: View and Manage Users
**Government user management screen**

### 3. Get All Registered Users
```
GET /api/v1/users/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "phone": "01712345678",
      "full_name": "John Doe",
      "role": "resident",
      "created_at": "2026-06-10T10:00:00Z"
    }
  ]
}
```

### 4. Get User Details
```
GET /api/v1/users/{user_id}/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

---

## Step 3: View User Bookings (Government view)
**See who's booked and when**

### 5. Get All Bookings
```
GET /api/v1/bookings/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user": 1,
      "hub": 1,
      "start_time": "2026-06-16T10:00:00Z",
      "end_time": "2026-06-16T12:00:00Z",
      "status": "upcoming"
    }
  ]
}
```

### 6. Get Booking Details
```
GET /api/v1/bookings/{booking_id}/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

---

## Step 4: Manage Hubs
**Manage open hubs allocation**

### 7. Get All Hubs
```
GET /api/v1/hubs/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Central Hub",
      "address": "Dhaka City",
      "status": "active",
      "battery_percentage": 92
    }
  ]
}
```

### 8. Update Hub Status
```
PATCH /api/v1/hubs/{hub_id}/status/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "status": "offline",
  "battery_percentage": 0
}
```

### 9. Assign Coordinator
```
PATCH /api/v1/hubs/{hub_id}/assign-coordinator/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "coordinator_id": "01799999999"
}
```

---

## Step 5: View Hazard Reports (Government view)
**Monitor all hazard reports**

### 10. Get All Hazards
```
GET /api/v1/hazards/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "category": "flood",
      "description": "Water on road",
      "latitude": 23.820,
      "longitude": 90.420,
      "severity": "medium",
      "status": "active"
    }
  ]
}
```

### 11. Get Hazard Details
```
GET /api/v1/hazards/{hazard_id}/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

### 12. Get Hazard Comments
```
GET /api/v1/hazards/{hazard_id}/comments/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

### 13. Cleanup Hazard Report
```
DELETE /api/v1/hazards/{hazard_id}/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

---

## Step 6: Monitor Check-ins
**Track residents arriving at hubs**

### 14. Get All Check-ins
```
GET /api/v1/checkins/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "hub": 1,
      "people_count": 3,
      "status": "safe",
      "timestamp": "2026-06-16T10:30:00Z"
    }
  ]
}
```

### 15. Get Check-in Details
```
GET /api/v1/checkins/{checkin_id}/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

---

## Step 7: Broadcast to Multiple Hubs
**Alert all residents**

### 16. Create Headline Broadcast
```
POST /api/v1/broadcasts/create/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "hub": 1,
  "subject": "PUBLIC ALERT",
  "body": "Flash flood warning in your area. Stay in safe zones.",
  "priority": "urgent"
}
```

### 17. Create Info Broadcast
```
POST /api/v1/broadcasts/create/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "hub": 1,
  "subject": "Information Update",
  "body": "Power restoration expected by 4 PM",
  "priority": "info"
}
```

### 18. Mark Broadcast as Read
```
POST /api/v1/broadcasts/{broadcast_id}/read/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "hub": 1
}
```

---

## Step 8: Manage Broadcasts
**Review and manage all broadcasts**

### 19. Get All Broadcasts
```
GET /api/v1/broadcasts/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
```

---

## Step 9: Invite Users to System
**Government user creation**

### 20. Invite Government Official
```
POST /api/v1/users/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "official@government.gov.bd",
  "full_name": "Government Official"
}
```

### 21. Invite Resident
```
POST /api/v1/users/
Authorization: Bearer YOUR_GOVERNMENT_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "phone": "01788888888",
  "full_name": "New Resident",
  "household_size": 3,
  "medical_needs": "heart_condition"
}
```

---

## Government Testing Checklist

Use this checklist for complete government workflow testing:

- [ ] **Dashboard Overview** — View all reports & stats
- [ ] **Map View** — View hazards on map
- [ ] **User Management** — Get all users
- [ ] **User Details** — View specific user info
- [ ] **Booking Monitoring** — View all bookings
- [ ] **Hub Management** — Update hub status
- [ ] **Coordinator Assignment** — Assign hub coordinators
- [ ] **Hazard Monitoring** — View all hazards
- [ ] **Hazard Comments** — View hazard discussions
- [ ] **Check-in Monitoring** — View check-ins
- [ ] **Broadcast Creation** — Make urgent announcements
- [ ] **Broadcast List** — View all broadcasts
- [ ] **User Invitations** — Invite government officials
- [ ] **Resident Invitations** — Register residents

---

## Government User Roles

| Role | Permissions | JWT Token Source |
|------|-------------|------------------|
| **Government Official** | View reports, manage hubs, broadcast | Login with gov email/phone |
| **Admin** | Full system control, everything above | User created by other admin |

---

## Complete Government Workflow

1. **Login** ✅ (gov@government.gov.bd / password)
2. **View Dashboard** — System overview ✅
3. **View Map** — Geo-view hazards & hubs ✅
4. **Monitor Users** — See registered residents ✅
5. **Monitor Bookings** — Track arrivals ✅
6. **Manage Hubs** — Status & coordinators ✅
7. **View Hazards** — Active reports & priorities ✅
8. **Monitor Check-ins** — Safety status ✅
9. **Create Broadcasts** — Alerts & info ✅
10. **Invite Users** — Add officials or residents ✅

---

## Government Dashboard Key Metrics

### Main Dashboard Metrics:
- **Total Residents Safe** — Count of safe check-ins
- **Active Hazards** — Currently reported incidents
- **Operational Hubs** — Working hubs count
- **Alerts Sent** — Total broadcasts sent
- **Total Booking Requests** — Pending requests
- **Avg Check-in Time** — Average arrival time

### Location Intelligence:
- Hub battery levels and status
- Hazard status & severity distribution
- Road access status
- Peak visit times

### Safety Metrics:
- Number of residents per hub
- Response times to hazards
- Occupancy rates
- Weather conditions

---

## Security & Compliance

Government data access must:
- ✅ Require government JWT token
- ✅ Track all government actions
- ✅ Follow data retention policies
- ✅ Support audit logging
- ✅ Maintain role-based access

---

## Government Portal Access

### Login Credentials (Example):
```
Email: gov_official@government.gov.bd
Password: gov123456789
```

### Alternative Method:
```
Phone: 018123456789
Password: gov123456789
```

---

## Common Government Use Cases

1. **Emergency Response**: Monitor hazard reports in real-time
2. **Resource Allocation**: View hub occupancy and status
3. **Public Communication**: Send broadcast alerts
4. **User Management**: Invite officials and manage residents
5. **Dashboard Reporting**: Generate safety statistics