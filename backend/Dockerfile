# syntax=docker/dockerfile:1
#
# Backend image: Flask API served by gunicorn.
# Build context is ./backend (see docker-compose.yml).
#
FROM python:3.11-slim

# Keep the image small and the logs unbuffered so `docker compose logs` is live.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_APP=wsgi.py

WORKDIR /app

# psycopg2-binary ships its own libpq, but libpq5 keeps `pg_isready`/psql style
# client tooling and runtime linking predictable; curl is used by the healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first so the (slow) pip layer is cached while app code changes.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the backend source (migrations included - they are run inside the container).
COPY . /app

# Run as an unprivileged user.
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Container-level healthcheck against the public health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:5000/api/v1/health || exit 1

# No secrets are baked into the image: every setting comes from the environment
# (DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, FRONTEND_ORIGIN, FLASK_ENV/CONFIG_NAME).
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "wsgi:app"]
