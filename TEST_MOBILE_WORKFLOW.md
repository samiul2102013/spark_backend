# Mobile (Resident) Workflow Tests

## Environment Variables

| Variable | Source |
|---|---|
| `{{base_url}}` | `http://spark.kodevio.com:8000/api/v1` |
| `{{access_token}}` | From OTP verify → `data.access` |
| `{{refresh_token}}` | From OTP verify → `data.refresh` |
| `{{phone}}` | `01856669532` |
| `{{hub_id}}` | From hubs list → `data.results[0].id` |
| `{{hazard_id}}` | From create hazard → `data.id` |
| `{{booking_id}}` | From create booking → `data.id` |
| `{{notification_id}}` | From notifications list → `data.results[0].id` |

---

## Users Table

### 1. Register
**POST** `{{base_url}}/auth/register/`
```json
{
  "phone": "{{phone}}",
  "full_name": "Test Resident",
  "household_size": 4,
  "medical_needs": "none",
  "latitude": 23.8,
  "longitude": 90.4
}
```

### 2. Verify OTP
**POST** `{{base_url}}/auth/otp/verify/`
```json
{"phone": "{{phone}}", "code": "000000"}
```
→ Extract `data.access` as `{{access_token}}`, `data.refresh` as `{{refresh_token}}`

### 3. View Profile
**GET** `{{base_url}}/users/profile/`
Header: `Authorization: Bearer {{access_token}}`

### 4. Update Profile
**PUT** `{{base_url}}/users/profile/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"full_name": "Updated Name", "household_size": 3}
```

### 5. Change Password
**PUT** `{{base_url}}/users/change-password/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"old_password": "oldpass123", "new_password": "newpass123", "confirm_password": "newpass123"}
```

---

## Auth

### 6. Login (email/password)
**POST** `{{base_url}}/auth/login/`
```json
{"username": "{{phone}}", "password": "your-password"}
```

### 7. Refresh Token
**POST** `{{base_url}}/auth/refresh/`
```json
{"refresh": "{{refresh_token}}"}
```

### 8. Logout
**POST** `{{base_url}}/auth/logout/`
```json
{"refresh": "{{refresh_token}}"}
```

### 9. Forgot Password
**POST** `{{base_url}}/auth/forgot-password/`
```json
{"identifier": "{{phone}}"}
```

### 10. Reset Password
**POST** `{{base_url}}/auth/reset-password/`
```json
{"identifier": "{{phone}}", "code": "000000", "new_password": "newpass123", "confirm_password": "newpass123"}
```

---

## Hubs Table

### 11. List Hubs
**GET** `{{base_url}}/hubs/?page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`
→ Extract `data.results[0].id` as `{{hub_id}}`

### 12. Hub Detail
**GET** `{{base_url}}/hubs/{{hub_id}}/`
Header: `Authorization: Bearer {{access_token}}`

### 13. Hub Resources
**GET** `{{base_url}}/hubs/{{hub_id}}/resources/`
Header: `Authorization: Bearer {{access_token}}`

### 14. Hub Check-ins
**GET** `{{base_url}}/hubs/{{hub_id}}/checkins/?date=2026-06-20`
Header: `Authorization: Bearer {{access_token}}`
> `date` param is optional (YYYY-MM-DD format)

### 15. Hub Broadcasts
**GET** `{{base_url}}/hubs/{{hub_id}}/broadcasts/`
Header: `Authorization: Bearer {{access_token}}`

---

## Hazards Table

### 16. List Hazards
**GET** `{{base_url}}/hazards/?status=active&category=flooding&page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`
> Available filters: `status` (active/cleared), `category` (flooding/fallen_tree/blocked_road/utility_pole/medical/fire/collapsed_building/power_line_down/landslide/other), `hub_id` (int), `period` (pre/post)

### 17. Report Hazard
**POST** `{{base_url}}/hazards/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"category": "flooding", "description": "Water rising on Main Street", "latitude": 23.81, "longitude": 90.41, "severity": 3, "period": "post"}
```
> Category values: `flooding`, `fallen_tree`, `blocked_road`, `utility_pole`, `medical`, `fire`, `collapsed_building`, `power_line_down`, `landslide`, `other`
> Severity values: `1` (Low), `2` (Medium), `3` (High)
> Period values: `pre`, `post`
→ Extract `data.id` as `{{hazard_id}}`

### 18. Hazard Detail
**GET** `{{base_url}}/hazards/{{hazard_id}}/`
Header: `Authorization: Bearer {{access_token}}`

### 19. Clear Hazard
**PATCH** `{{base_url}}/hazards/{{hazard_id}}/clear/`
Header: `Authorization: Bearer {{access_token}}`

### 20. Delete Hazard
**DELETE** `{{base_url}}/hazards/{{hazard_id}}/`
Header: `Authorization: Bearer {{access_token}}`

---

## Comments Table

### 21. List Comments
**GET** `{{base_url}}/hazards/{{hazard_id}}/comments/?page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`

### 22. Add Comment
**POST** `{{base_url}}/hazards/{{hazard_id}}/comments/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"body": "Water level increasing rapidly"}
```
> Do not send `hazard` or `author` — they are auto-populated from the URL and auth context.

---

## Checkins Table

### 23. Check In
**POST** `{{base_url}}/checkins/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"hub": {{hub_id}}, "people_count": 4, "status": "safe", "road_access": "open"}
```
> Status values: `safe`, `need_assistance`
> Road access values: `open`, `blocked`, `unknown`

### 24. Check-in History
**GET** `{{base_url}}/checkins/history/?page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`
> Optional filters: `hub_id`, `status` (safe/need_assistance), `date` (YYYY-MM-DD)

### 25. Latest Check-in
**GET** `{{base_url}}/checkins/latest/`
Header: `Authorization: Bearer {{access_token}}`

---

## Bookings Table

### 26. Available Slots
**GET** `{{base_url}}/bookings/slots/?hub_id={{hub_id}}&date=2026-06-20`
Header: `Authorization: Bearer {{access_token}}`
> Both `hub_id` and `date` (YYYY-MM-DD) are required.

### 27. Create Booking
**POST** `{{base_url}}/bookings/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"hub": {{hub_id}}, "start_time": "2026-06-20T10:00:00-05:00", "end_time": "2026-06-20T12:00:00-05:00", "people_count": 2}
```
→ Extract `data.id` as `{{booking_id}}`

### 28. My Bookings
**GET** `{{base_url}}/bookings/?status=active&page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`
> Optional filters: `status` (active/cancelled/completed), `hub_id`

### 29. Cancel Booking
**PATCH** `{{base_url}}/bookings/{{booking_id}}/cancel/`
Header: `Authorization: Bearer {{access_token}}`

---

## Broadcasts Table

### 30. List Broadcasts
**GET** `{{base_url}}/broadcasts/?hub_id={{hub_id}}&page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`

---

## Notifications Table

### 31. List Notifications
**GET** `{{base_url}}/notifications/?unread_only=true&page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`
> `unread_only` accepts `true`/`1` to filter unread only.

### 32. Mark Read
**PATCH** `{{base_url}}/notifications/{{notification_id}}/read/`
Header: `Authorization: Bearer {{access_token}}`

### 33. Mark All Read
**POST** `{{base_url}}/notifications/read-all/`
Header: `Authorization: Bearer {{access_token}}`
