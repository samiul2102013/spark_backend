# Phase 1 — Project Scaffolding & Infrastructure

## Goal
Set up the complete backend foundation: Django project structure, Docker environment (PostgreSQL, Redis, Nginx), CI/CD pipeline, and all config files — zero business logic, just infrastructure that boots and passes health checks.

## What we will build

### 1. Django Project Scaffolding
- `config/` — split settings (`base.py`, `local.py`, `production.py`), `celery.py`, `urls.py`, `wsgi.py`, `asgi.py`
- `core/` — shared foundations: `models.py` (TimeStampedModel), `exceptions.py`, `responses.py`, `permissions.py`, `middleware.py`
- `apps/users/` — Custom User model (AbstractBaseUser, phone_number primary)
- `apps/hubs/` — Hub model placeholder
- `apps/hazards/` — Hazard model placeholder
- `apps/bookings/` — Booking model placeholder
- `apps/comms/` — Comms app placeholder
- `apps/ai/` — AI app placeholder
- `apps/sync/` — SyncLog model + batch endpoint placeholder
- `shared/` — Cross-app utils placeholder

### 2. Docker Environment
- `Dockerfile` — Multi-stage: build → production (Python 3.12, uv/pip)
- `docker-compose.yml` — Services: Django, PostgreSQL 16, Redis 7, Nginx
- `nginx/nginx.conf` — Reverse proxy: static/media serving, proxy to Django

### 3. CI/CD Pipeline (GitHub Actions)
- `.github/workflows/deploy.yml`
  - On push to `main` branch
  - Lint + type check
  - Build Docker images
  - Deploy to VPS via SSH + docker-compose pull/up

### 4. Configuration Files
- `.env.example` — All secrets templated
- `requirements.txt` — Production deps
- `requirements-dev.txt` — Dev deps (black, ruff, mypy, pytest)
- `.dockerignore`
- `.gitignore`

### 5. Health Check
- `GET /api/v1/health/` — Returns `{"status": "success", "data": {"db": "ok", "redis": "ok"}}`

## What we will NOT build (Phase 1)
- No business logic / CRUD endpoints for any app
- No authentication endpoints (Phase 2)
- No external API adapters (Phase 3+)
- No offline sync conflict resolution (Phase 4+)
- No tests (add in Phase 2)

## Deliverables
- Working `docker-compose up` with all services green
- `curl localhost/api/v1/health/` returns 200
- GitHub Actions pipeline ready (needs repo + secrets to activate)
- VPS deployment steps documented

---

## VPS Deployment Guide

### Prerequisites
- VPS with Ubuntu 22.04+ (min $10/mo: 2GB RAM, 2 vCPU, 50GB SSD)
- Docker & Docker Compose installed on VPS
- Domain (optional) pointing to VPS IP
- GitHub repository created with `main` branch pushed

### Step 1: Initial VPS Setup
```bash
# SSH into your VPS
ssh user@your-vps-ip

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Log out and back in for group to take effect

# Install Docker Compose
sudo apt update && sudo apt install -y docker-compose-plugin

# Create deploy directory
sudo mkdir -p /opt/spark-backend
sudo chown $USER:$USER /opt/spark-backend
```

### Step 2: Clone and Configure
```bash
cd /opt/spark-backend
git clone https://github.com/YOUR_ORG/chargesafe-backend.git .
git checkout main

# Create .env from example
cp spark_backend/.env.example spark_backend/.env
nano spark_backend/.env
# Fill in: SECRET_KEY, DB passwords, API keys etc.
```

### Step 3: Set Required Env Vars
| Variable | Value |
|----------|-------|
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` |
| `CORS_ALLOWED_ORIGINS` | `https://yourdomain.com,https://admin.yourdomain.com` |
| `SECRET_KEY` | Generate with `openssl rand -hex 64` |
| `POSTGRES_PASSWORD` | Strong random password |

### Step 4: Launch Services
```bash
cd /opt/spark-backend/spark_backend
docker compose up -d --build

# Verify all containers are running
docker compose ps

# Run migrations (if first time)
docker compose exec django python manage.py migrate

# Create admin user
docker compose exec django python manage.py createsuperuser

# Verify health endpoint
curl http://localhost/api/v1/health/
# Expected: {"status":"success","data":{"db":"ok","redis":"ok"},"message":"Health check"}
```

### Step 5: Set Up Nginx SSL (Let's Encrypt)
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### Step 6: Configure GitHub Secrets for CI/CD
Go to your repo → Settings → Secrets and variables → Actions → Add these:

| Secret | Value |
|--------|-------|
| `VPS_HOST` | Your VPS IP or domain |
| `VPS_USER` | SSH username |
| `VPS_SSH_KEY` | Private SSH key (copy from `~/.ssh/id_rsa`) |
| `VPS_PORT` | `22` (or your custom SSH port) |

### Step 7: Push to Auto-Deploy
```bash
git add .
git commit -m "Phase 1: project scaffolding"
git push origin main
# GitHub Actions will: lint → build → ssh into VPS → git pull → docker compose up
```

### Useful Commands (Post-Deploy)
```bash
# View logs
docker compose logs -f django
docker compose logs -f nginx

# Execute Django commands
docker compose exec django python manage.py migrate
docker compose exec django python manage.py collectstatic

# Rebuild after config changes
docker compose up -d --build --remove-orphans

# Backup database
docker compose exec db pg_dump -U spark spark > backup_$(date +%Y%m%d).sql
```
