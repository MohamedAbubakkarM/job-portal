"""Container settings for the free-tier deployment (Render + Neon + Sentry).

settings_server.py is hard-wired to peeljobs.com, S3 and SES. This module keeps
every deployment-specific value in environment variables instead, so the same
image runs under docker-compose locally and on Render.

Known ceilings of the free tier, each with its upgrade path:
- MEDIA_ROOT is the container disk, wiped on every redeploy. Uploaded resumes
  and logos do not survive; point DEFAULT storage at S3/R2 to keep them.
- Celery runs tasks inline (no broker, no worker), and beat schedules never
  fire. Add Redis + a worker service to get them back.
"""

import os

import sentry_sdk

from .settings import *
from .settings import BASE_DIR, DATABASES, MIDDLEWARE, env_bool

DEBUG = env_bool("DEBUG", False)
TEMPLATE_DEBUG = DEBUG

# Comma-separated, e.g. "peeljobs-api.onrender.com,localhost"
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost").split(",") if h.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

# Render terminates TLS and forwards X-Forwarded-Proto. docker-compose serves
# plain HTTP, so it sets SECURE_SSL_REDIRECT=False.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = 3600 if SECURE_SSL_REDIRECT else 0

# Neon requires TLS; the local compose Postgres does not.
DATABASES["default"]["OPTIONS"]["sslmode"] = os.getenv("DB_SSLMODE", "prefer")
DATABASES["default"]["CONN_MAX_AGE"] = 60

# WhiteNoise serves /static/ (Django admin, API docs) straight from gunicorn.
MIDDLEWARE = [
    MIDDLEWARE[0],
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
COMPRESS_ENABLED = False

CELERY_TASK_ALWAYS_EAGER = True

# Console backend prints emails to the service logs. For real delivery set
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend and the SMTP vars
# (Brevo's free plan: smtp-relay.brevo.com:587, 300 mails/day).
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True

# One line per log record on stdout, which is what Render's log viewer reads.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(levelname)s %(name)s %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
    "loggers": {"django.db.backends": {"level": "WARNING"}},
}

# No-op when SENTRY_DSN is unset.
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
    release=os.getenv("APP_VERSION"),
    traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
)
