from .base import *  # noqa
import os

DEBUG = False

ENABLE_HTTPS = os.getenv("ENABLE_HTTPS", "False") == "True"

if ENABLE_HTTPS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://spark.kodevio.com:8000",
    "https://spark.kodevio.com",
    "https://spark-admin-dashboard.vercel.app",
    "https://spark-dashboard-xi.vercel.app",
    "https://api.sparkcentra.com",
    "https://admin.sparkcentra.com",
    "https://gov.sparkcentra.com",
]

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
