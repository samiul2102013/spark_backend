# Admin Workflow Tests

## Environment Variables

| Variable | Source |
|---|---|
| `{{base_url}}` | `http://spark.kodevio.com:8000/api/v1` |
| `{{access_token}}` | From login response → `data.access` |
| `{{phone}}` | `01856669532` |
| `{{hub_id}}` | From create hub response → `data.id` |
| `{{message_id}}` | From list messages response → `data.results[0].id` |
| `{{hazard_id}}` | From create hazard → `data.id` |

---

### 1. Login as Admin
**POST** `{{base_url}}/auth/login/`
```json
{"username": "admin@spark.gov", "password": "your-admin-password"}
```
→ Extract `data.access` as `{{access_token}}`

---

### 2. Create Coordinator
**POST** `{{base_url}}/admin/users/invite/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"phone_number": "01856669533", "full_name": "Test Coordinator", "role": "coordinator", "hub_id": null}
```

---

### 3. Create Hub
**POST** `{{base_url}}/hubs/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"name": "Main Shelter", "address": "Downtown", "latitude": 23.8, "longitude": 90.4, "status": "open", "max_concurrent_bookings": 10}
```
→ Extract `data.id` as `{{hub_id}}`

---

### 4. Assign Coordinator to Hub
**PATCH** `{{base_url}}/admin/hubs/{{hub_id}}/assign-coordinator/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"coordinator_id": "01856669533"}
```

---

### 5. List Residents
**GET** `{{base_url}}/admin/residents/?page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`

---

### 6. Resident Detail
**GET** `{{base_url}}/admin/residents/{{phone}}/`
Header: `Authorization: Bearer {{access_token}}`

---

### 7. List Coordinators
**GET** `{{base_url}}/admin/coordinators/?page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`

---

### 8. Suspend / Activate User
**PATCH** `{{base_url}}/admin/residents/{{phone}}/suspend/`
Header: `Authorization: Bearer {{access_token}}`

**PATCH** `{{base_url}}/admin/residents/{{phone}}/activate/`
Header: `Authorization: Bearer {{access_token}}`

---

### 9. Change User Role
**PATCH** `{{base_url}}/admin/users/{{phone}}/role/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"role": "coordinator"}
```

---

### 10. Create Broadcast
**POST** `{{base_url}}/broadcasts/create/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"hub": {{hub_id}}, "subject": "Emergency Alert", "body": "Storm approaching", "priority": "urgent"}
```
> Priority values: `info`, `warning`, `urgent`

---

### 11. List Inbound Messages
**GET** `{{base_url}}/admin/messages/?page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`

---

### 12. Message Detail
**GET** `{{base_url}}/admin/messages/{{message_id}}/`
Header: `Authorization: Bearer {{access_token}}`

---

### 13. Classify Message
**PATCH** `{{base_url}}/admin/messages/{{message_id}}/classify/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"hazard_id": {{hazard_id}}}
```

---

### 14. Admin Overview
**GET** `{{base_url}}/admin/overview/`
Header: `Authorization: Bearer {{access_token}}`

---

### 15. AI Config
**GET** `{{base_url}}/admin/ai-config/`
Header: `Authorization: Bearer {{access_token}}`

**PUT** `{{base_url}}/admin/ai-config/`
Header: `Authorization: Bearer {{access_token}}`
```json
{"auto_reporting_enabled": true, "report_interval_minutes": 30}
```
