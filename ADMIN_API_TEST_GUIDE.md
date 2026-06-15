# Admin API Testing Guide

**Complete System Administrator API**

**Base URL**: `http://spark.kodevio.com:8000/api/v1/`

**Authentication**: Admin role JWT token (superuser privileges)

---

## Step 1: Admin Dashboard Overview
**Complete system overview**

### 1. View System Statistics
```
GET /api/v1/dashboard/reports/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "total_users": 150,
    "active_hubs": 8,
    "pending_bookings": 12,
    "active_hazards": 5,
    "completed_tasks_today": 9
  }
}
```

### 2. View Active Sessions
```
GET /api/v1/dashboard/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

---

## Step 2: Complete User Management
**Full control over all users**

### 3. List All Users
```
GET /api/v1/users/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
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
      "email": "john@example.com",
      "role": "resident",
      "household_size": 4,
      "created_at": "2026-06-10T10:00:00Z"
    }
  ]
}
```

### 4. Get User Details
```
GET /api/v1/users/{user_id}/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "phone": "01712345678",
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "resident",
    "household_size": 4,
    "medical_needs": "diabetes"
  }
}
```

### 5. Update User Profile
```
PUT /api/v1/users/{user_id}/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "full_name": "John Smith",
  "email": "john.smith@example.com",
  "household_size": 5,
  "medical_needs": "hypertension"
}
```

### 6. Change User Password
```
PUT /api/v1/users/change-password/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "old_password": "oldpass123",
  "new_password": "newpass456",
  "confirm_password": "newpass456"
}
```

---

## Step 3: Manage User Roles
**Change any user's role**

### 7. Set User as Resident
```
PATCH /api/v1/admin/users/01712345678/set-role/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "role": "resident"
}
```

### 8. Set User as Coordinator
```
PATCH /api/v1/admin/users/01712345678/set-role/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "role": "coordinator"
}
```

### 9. Set User as Admin
```
PATCH /api/v1/admin/users/01712345678/set-role/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "role": "admin"
}
```

---

## Step 4: Invite New Users
**Create new administrators**

### 10. Invite New Admin
```
POST /api/v1/admin/users/invite/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "newadmin@gov.gov.bd",
  "full_name": "Admin Name"
}
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "user_id": 2,
    "email": "newadmin@gov.gov.bd",
    "role": "admin",
    "invited_at": "2026-06-16T10:00:00Z"
  }
}
```

### 11. Invite Coordinator
```
POST /api/v1/admin/users/invite/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "coordinator@hub1.gov.bd",
  "full_name": "Hub Coordinator"
}
```

### 12. Invite Resident
```
POST /api/v1/admin/users/invite/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "phone": "01744444444",
  "full_name": "New Resident",
  "household_size": 2,
  "medical_needs": "asthma"
}
```

---

## Step 5: Delete Users
**Remove unwanted users**

### 13. Delete User
```
DELETE /api/v1/admin/users/01712345678/delete/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

---

## Step 6: Hub Management
**Complete hub control**

### 14. List All Hubs
```
GET /api/v1/hubs/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

### 15. Get Hub Details
```
GET /api/v1/hubs/1/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

### 16. Update Hub Info
```
PATCH /api/v1/hubs/1/update/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "Updated Hub Name",
  "address": "New address",
  "max_concurrent_bookings": 10
}
```

### 17. Delete Hub
```
DELETE /api/v1/hubs/1/delete/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

### 18. Update Hub Status
```
PATCH /api/v1/hubs/1/status/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "status": "offline",
  "battery_percentage": 0
}
```

---

## Step 7: Hazard Management
**Complete hazard control**

### 19. List All Hazards
```
GET /api/v1/hazards/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

### 20. Get Hazard Details
```
GET /api/v1/hazards/1/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

### 21. Update Hazard
```
PATCH /api/v1/hazards/1/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "severity": "critical",
  "status": "resolved"
}
```

### 22. Clear Hazard Report
```
DELETE /api/v1/hazards/1/delete/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

---

## Step 8: Complete Booking Control
**Full booking management**

### 23. View All Bookings
```
GET /api/v1/bookings/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

### 24. Get Booking Details
```
GET /api/v1/bookings/1/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

### 25. Complete Booking
```
PATCH /api/v1/bookings/1/complete/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "check_in_time": "2026-06-16T10:30:00Z",
  "people_count": 3
}
```

---

## Step 9: Complete Broadcast Control
**Full broadcast management**

### 26. View All Broadcasts
```
GET /api/v1/broadcasts/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

### 27. Delete Broadcast
```
DELETE /api/v1/broadcasts/1/delete/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

### 28. Mark Broadcast as Read
```
POST /api/v1/broadcasts/1/read/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json
```

---

## Step 10: Check-in Management
**View all check-ins**

### 29. View All Check-ins
```
GET /api/v1/checkins/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

---

## Step 11: Monitors & Analytics
**System monitoring**

### 30. View System Health
```
GET /api/v1/health/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "db": "ok",
    "redis": "ok",
    "mem_usage": "45%",
    "gpu_usage": "10%"
  }
}
```

### 31. View API Schema
```
GET /api/v1/schema/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```
**(Swagger documentation endpoint)**

---

## Admin Testing Checklist

Use this complete admin workflow checklist:

- [ ] **Dashboard Overview** — System statistics
- [ ] **User Management** — List, view, update users
- [ ] **Role Management** — Set admin, coordinator, resident roles
- [ ] **User Deletion** — Remove unwanted users
- [ ] **Admin Invitation** — Create new admin users
- [ ] **Coordinator Invitation** — Create coordinators
- [ ] **Resident Invitation** — Create residents
- [ ] **Hub Management** — CRUD operations
- [ ] **Hazard Management** — CRUD operations
- [ ] **Booking Management** — View, complete bookings
- [ ] **Broadcast Management** — Delete broadcasts
- [ ] **Check-in Management** — View all check-ins
- [ ] **System Health** — Monitor server status
- [ ] **API Documentation** — View schema

---

## Complete Admin Workflow

1. **Login** ✅ (admin@test.com / admin1234)
2. **Dashboard** — Overview stats
3. **Users** — Manage all users
4. **Roles** — Assign roles & permissions
5. **Invitations** — Invite new users
6. **Hubs** — Manage hub operations
7. **Hazards** — Monitor & resolve hazards
8. **Bookings** — View & manage bookings
9. **Broadcasts** — Manage public alerts
10. **Check-ins** — Monitor arrivals
11. **Health** — System monitoring
12. **Schema** — API documentation

---

## Admin User Creation

### Initial Admin Setup:

```
Email: admin@test.com
Password: admin1234
Role: admin
```

### Create Admin via API:
```
POST /api/v1/admin/users/invite/
Authorization: Bearer YOUR_INITIAL_ADMIN_TOKEN
Content-Type: application/json

{
  "email": "superadmin@government.gov.bd",
  "full_name": "Super Administrator"
}
```

---

## Admin Security Levels

| Level | Permissions | Action Required |
|-------|-------------|-----------------|
| **Level 1: Government** | View all, moderate changes | Invitation |
| **Level 2: Admin** | Full access to all resources | Manual invite |
| **Level 3: Super Admin** | System-level control | Current role |

---

## Admin Key Responsibilities

### User Management:
- Create new administrators and coordinators
- Assign roles based on responsibility
- Monitor user activity and permissions
- Remove suspended or unwanted users

### System Configuration:
- Configure hub operations
- Set hub capacity limits
- Manage hub coordinators
- Monitor hub performance

### Emergency Response:
- View all hazard reports in real-time
- Update hazard severity and status
- Coordinate response teams
- Monitor system-wide safety metrics

### Reporting:
- Generate system statistics
- Track user engagement
- Monitor booking patterns
- Analyze safety response times

---

## Common Admin Use Cases

1. **New Admin Onboarding**: Invite new admin users
2. **User Management**: Update roles and permissions
3. **Hub Setup**: Configure new hubs in the system
4. **Emergency Response**: Monitor and manage hazard reports
5. **Audit Trail**: Review all user actions
6. **Data Management**: Delete old user accounts
7. **System Monitoring**: Monitor health and performance
8. **Broadcast Control**: Remove inappropriate broadcasts

---

## Admin Actions with Logging

Every admin action is logged:
- [ ] User creation
- [ ] Role changes
- [ ] Hub configuration updates
- [ ] Hazard management actions
- [ ] Booking modifications
- [ ] Broadcast deletions
- [ ] Password changes

---

## Audit Trail Requirements

All admin actions tracked:
- Timestamp of action
- Admin user ID
- Action type
- Target resource
- Previous and new values
- IP address

---

## Admin Portal Access

### Initial Admin Credentials:
```
Email: admin@test.com
Password: admin1234
```

### Alternative Method:
```
Phone: admin@test.com (if using phone as primary)
Password: admin1234
```

---

## Security Considerations

Admin APIs require:
- ✅ Admin role verification
- ✅ Multi-factor authentication (optional)
- ✅ Operation audit logs
- ✅ IP whitelisting
- ✅ Rate limiting
- ✅ Session timeout

---

## High-Risk Admin Operations

Operations requiring confirmation:
1. **User Deletion** — Confirm before delete
2. **Role Changes** — Show user impact
3. **Hub Deletion** — Verify no bookings
4. **Broadcast Deletion** — Confirm public notice
5. **Data Deletion** — Permanent removal

---

## Admin Performance Metrics

Monitor admin actions:
- User creation rate
- Role changes per day
- Hub configuration frequency
- Hazard update volume
- System response times

---

## Complete Administrator Powers

1. **Complete Access**: All system resources
2. **User Control**: Create, modify, delete
3. **Role Management**: Assign all roles
4. **System Monitoring**: View all metrics
5. **Audit Trail**: Review all actions
6. **API Access**: Full schema access
7. **Emergency Control**: Override any action
8. **Data Management**: Complete data control

---

## End-to-End Admin Workflow

1. **Login** → Authenticate as Super Admin
2. **Dashboard** → View system overview
3. **Create Admin** → Add new administrators
4. **Create Coordinator** → Designate hub coordinators
5. **Configure Hubs** → Add new operational hubs
6. **Monitor Users** → Review all registered users
7. **Manage Roles** → Assign roles based on workflow
8. **Track Emergencies** → Monitor hazards in real-time
9. **Simplify Operations** → Update hazard status
10. **Monitor Operations** → View bookings and check-ins
11. **Broadcast Alerts** → Send emergency messages
12. **Audit Actions** → Review all system activities
13. **Monitor Health** → Check service status
14. **View Documentation** → Access API schema

This complete admin workflow covers all system capabilities and provides full oversight of the ChargeSafe platform.