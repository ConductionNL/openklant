# OpenKlant ExApp for Nextcloud
# Wraps OpenKlant customer interaction registry with AppAPI integration
#
# OpenKlant is part of the Common Ground ecosystem for Dutch municipalities.
# It requires:
# - PostgreSQL database
# - Redis for caching (optional)
#
# See: https://github.com/maykinmedia/open-klant

# Use upstream OpenKlant image as base (already has Django, uwsgi, etc.)
FROM maykinmedia/open-klant:2.2.0

# Install additional dependencies for ExApp wrapper
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for ExApp wrapper (FastAPI, uvicorn, httpx)
RUN pip install --no-cache-dir \
    "fastapi>=0.109.0" \
    "uvicorn>=0.27.0" \
    "httpx>=0.26.0"

# Copy ExApp wrapper
COPY ex_app /app/ex_app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create directories for media and static files
RUN mkdir -p /app/media /app/static /app/log && \
    chown -R nobody:nogroup /app/media /app/static /app/log

WORKDIR /app

# Environment variables (set by AppAPI)
ENV APP_HOST=0.0.0.0
ENV APP_PORT=9000
ENV PYTHONUNBUFFERED=1

# OpenKlant configuration
ENV OPENKLANT_PORT=8000
ENV DJANGO_SETTINGS_MODULE=openklant.conf.docker

# OpenKlant requires these to be set (defaults for development)
ENV DB_HOST=localhost
ENV DB_NAME=openklant
ENV DB_USER=openklant
ENV DB_PASSWORD=openklant
ENV SECRET_KEY=change-me-in-production
ENV ALLOWED_HOSTS=*

# Expose ports: 9000 for AppAPI, 8000 for OpenKlant
EXPOSE 9000 8000

# Health check - just verify the wrapper is responding (any status is ok during init)
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD curl -s http://localhost:${APP_PORT:-9000}/heartbeat | grep -q status || exit 1

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
