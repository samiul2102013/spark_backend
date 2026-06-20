# AGENTS.md — ChargeSafe

## Stack
- Python 3.12+, Django 5.0, Django REST Framework, drf-spectacular (OpenAPI)
- PostgreSQL, Redis, Celery
- Apps: users, hubs, hazards, bookings, comms, ai, sync, dashboard, admin_api

## Developer commands
```bash
# Run dev server
python spark_backend/manage.py runserver

# Run tests (all)
python spark_backend/manage.py test

# Run tests (single app)
python spark_backend/manage.py test apps.hazards

# Generate migrations
python spark_backend/manage.py makemigrations

# Apply migrations
python spark_backend/manage.py migrate

# Generate OpenAPI schema (full)
python spark_backend/manage.py spectacular --file schema.yml
```

## API docs
- Swagger UI: `GET /api/v1/docs/`
- Full schema: `GET /api/v1/schema/`
- Mobile-only: `GET /api/v1/docs/mobile/`
- Dashboard-only: `GET /api/v1/docs/dashboard/`

## API conventions
- All endpoints prefixed with `/api/v1/`
- Auth: Bearer JWT (SimpleJWT, keyed on `phone_number`)
- Response envelope: `{"status": "success"|"error", "data": ..., "message": ...}`
- Pagination: page-based (`page`, `limit` params, default 20, max 100)
- Read-only fields (`hazard` on Comment, `reporter` on Hazard, `author` on Comment) are auto-populated from the request context / URL — do not send in the body.

## Schema documentation
- Use `@extend_schema` on every view method with `summary`, `description`, `parameters` (with `enum` for choices), `request`, `responses`, and `examples`.
- Define choice lists as module-level constants (e.g., `HAZARD_CATEGORIES`) and pass them as `enum=` to `OpenApiParameter`.
- Use `OpenApiExample` to provide concrete request body examples.
