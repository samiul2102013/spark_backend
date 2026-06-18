# Dashboard (Government) Workflow Tests

## Environment Variables

| Variable | Source |
|---|---|
| `{{base_url}}` | `http://spark.kodevio.com:8000/api/v1` |
| `{{access_token}}` | From login response → `data.access` |
| `{{hub_id}}` | From create hub → `data.id` |
| `{{phone}}` | `01856669532` |

---

### 1. Login
**POST** `{{base_url}}/auth/login/`
```json
{"username": "{{phone}}", "password": "..."}
```
→ Extract `data.access` as `{{access_token}}`

---

### 2. Overview
**GET** `{{base_url}}/dashboard/overview/`
Header: `Authorization: Bearer {{access_token}}`

---

### 3. Map
**GET** `{{base_url}}/dashboard/map/`
Header: `Authorization: Bearer {{access_token}}`

---

### 4. Reports
**GET** `{{base_url}}/dashboard/reports/`
Header: `Authorization: Bearer {{access_token}}`

---

### 5. Alerts
**GET** `{{base_url}}/dashboard/alerts/`
Header: `Authorization: Bearer {{access_token}}`

---

### 6. Infrastructure List
**GET** `{{base_url}}/dashboard/infrastructure/`
Header: `Authorization: Bearer {{access_token}}`

---

### 7. Infrastructure Detail
**GET** `{{base_url}}/dashboard/infrastructure/{{hub_id}}/`
Header: `Authorization: Bearer {{access_token}}`
