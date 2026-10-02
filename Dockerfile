# ACEest Fitness & Gym - Flask application image
FROM python:3.12-slim

# Keep Python output unbuffered and skip .pyc files in the image.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

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

# Serve with gunicorn (production WSGI server). `app:app` is the Flask
# instance created by the application factory in app.py.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
