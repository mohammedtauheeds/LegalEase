# ==============================================================================
# LegalEase - Production Multi-Stage Dockerfile
# Base Image: Official Python 3.11 Slim (Debian Bookworm)
# ==============================================================================

FROM python:3.11-slim as base

# 1. Prevent Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000 \
    HOST=0.0.0.0

# 2. Set working directory
WORKDIR /app

# 3. Install required OS packages for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Create non-root application user for container security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# 6. Copy application source code (excluding items in .dockerignore)
COPY . /app

# 7. Create instance directory for persistent SQLite database and set ownership
RUN mkdir -p /app/instance && \
    chown -R appuser:appuser /app

# 8. Switch to non-root user
USER appuser

# 9. Expose application port
EXPOSE 5000

# 10. Container Healthcheck via /api/health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:5000/api/health || exit 1

# 11. Run production WSGI application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "60", "wsgi:app"]
