# ACEest Fitness & Gym - Flask application image
FROM python:3.12-slim

# Release metadata, injected by CI, e.g.:
#   docker build --build-arg APP_VERSION=1.1.0 --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) .
ARG APP_VERSION=1.1.0
ARG GIT_COMMIT=unknown

# OCI labels. image.source links the GHCR package to the GitHub repository.
LABEL org.opencontainers.image.title="aceest-fitness" \
      org.opencontainers.image.description="ACEest Fitness & Gym Flask application" \
      org.opencontainers.image.source="https://github.com/2025tm93127-rohanbits/ACEAST-Fitness" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}"

# Keep Python output unbuffered, skip .pyc files, and expose release metadata
# to the app (served on /version and in the page footer).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_VERSION=${APP_VERSION} \
    GIT_COMMIT=${GIT_COMMIT}

WORKDIR /app

# Install dependencies first (better layer caching).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source.
COPY . .

# Store the SQLite database in a dedicated, writable location.
ENV ACEEST_DB=/app/data/aceest_fitness.db
RUN mkdir -p /app/data

# Run as a non-root user.
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Container-level health check against /health (Kubernetes uses its own
# liveness/readiness probes; this covers plain `docker run`).
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2).status == 200 else 1)"

# Serve with gunicorn (production WSGI server). `app:app` is the Flask
# instance created by the application factory in app.py.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
