# SPARK — VPS Deployment Guide

## Prerequisites on VPS

```bash
ssh root@<VPS_IP>

# Install Docker (if not installed)
curl -fsSL https://get.docker.com | sh

# Verify
docker --version && docker compose version
```

---

## 1. Clone the repo

```bash
cd /opt
git clone https://github.com/samiul2102013/spark_backend.git spark
cd spark
```

---

## 2. Configure environment

```bash
cp .env.example .env
nano .env
```

Fill these values:

```
SECRET_KEY=generate-a-long-random-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,spark.kodevio.com
CORS_ALLOWED_ORIGINS=https://spark.kodevio.com
DATABASE_URL=postgres://spark:spark@db:5432/spark
CELERY_BROKER_URL=redis://redis:6379/0
REDIS_URL=redis://redis:6379/1
DJANGO_SETTINGS_MODULE=config.settings.production
```

Generate a secret key: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`

---

## 3. Set up nginx for the domain

```bash
nano /etc/nginx/sites-available/spark.kodevio.com
```

```
server {
    listen 80;
    server_name spark.kodevio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/spark/staticfiles/;
    }

    location /media/ {
        alias /opt/spark/media/;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/spark.kodevio.com /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

> If using Apache instead, skip nginx. The Docker nginx container can also handle it (see step 4 note).

---

## 4. Start the stack

```bash
docker compose up -d --build
```

This starts: PostgreSQL, Redis, Django (gunicorn), Celery Worker, Celery Beat, and Nginx.

> **Port 80 note**: If the VPS already has Apache/nginx on port 80, edit `docker-compose.yml` and change the nginx service port from `"80:80"` to `"8000:80"`, then let the system nginx proxy to `127.0.0.1:8000` (matching step 3). Or remove the Docker nginx entirely and use only the system nginx.

---

## 5. Verify

```bash
curl http://localhost/api/v1/health/
# → {"status":"success","data":{"db":"ok","redis":"ok"},"message":"Health check"}

curl http://spark.kodevio.com/api/v1/health/
# → same
```

---

## 6. Seed initial admin user

```bash
docker compose exec django python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(
    full_name='Admin',
    email='admin@spark.gov',
    password='<strong-password>',
    role='admin',
    is_active=True,
)
"
```

---

## 7. Set up SSL (Let's Encrypt)

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d spark.kodevio.com
```

---

## GitHub Actions (optional, for auto-deploy)

Set these secrets in your repo → Settings → Secrets and variables → Actions:

| Secret | Value |
|--------|-------|
| `SSH_HOST` | VPS IP address |
| `SSH_USER` | root |
| `SSH_KEY` | Your SSH private key |
| `SSH_PORT` | 22 |

Then pushing to `main` will auto-deploy via `.github/workflows/deploy.yml`.
