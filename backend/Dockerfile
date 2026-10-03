# Django API image. Build context: backend/
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=jobsp.settings_cloud \
    PORT=8000

WORKDIR /app

# Dependencies first so code edits don't bust this layer.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY . .

# collectstatic needs a SECRET_KEY to import settings, not a real one.
RUN SECRET_KEY=build-only python manage.py collectstatic --noinput

# Git SHA of the build, reported by /health/ and to Sentry as the release.
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION

RUN useradd --create-home app && mkdir -p media && chown -R app media
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(urllib.request.Request(f'http://localhost:{os.environ[\"PORT\"]}/health/', headers={'X-Forwarded-Proto': 'https'}), timeout=4)"

# Render's free tier has no pre-deploy hook, so migrations run at start-up.
CMD python manage.py migrate --noinput && \
    exec gunicorn jobsp.wsgi --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-2} --access-logfile -
