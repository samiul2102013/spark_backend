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
**GET** `{{base_url}}/dashboard/map/?lat_min=17.8&lat_max=18.6&lng_min=-77.4&lng_max=-76.5`
Header: `Authorization: Bearer {{access_token}}`
> Bounding box params (`lat_min`, `lat_max`, `lng_min`, `lng_max`) are optional — omit to get all data.

---

### 4. Reports
**GET** `{{base_url}}/dashboard/reports/?hub_id={{hub_id}}&page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`

---

### 5. Alerts
**GET** `{{base_url}}/dashboard/alerts/?severity=2&status=active&hub_id={{hub_id}}&page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`
> Severity values: `1` (Low), `2` (Medium), `3` (High)
> Status values: `active`, `cleared`

---

### 6. Infrastructure List
**GET** `{{base_url}}/dashboard/infrastructure/?page=1&limit=20`
Header: `Authorization: Bearer {{access_token}}`

---

### 7. Infrastructure Detail
**GET** `{{base_url}}/dashboard/infrastructure/{{hub_id}}/`
Header: `Authorization: Bearer {{access_token}}`
