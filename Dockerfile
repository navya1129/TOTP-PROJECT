# -------- Stage 1: Builder --------
FROM python:3.11-slim AS builder

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------- Stage 2: Runtime --------
FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
 && rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata

COPY --from=builder /usr/local /usr/local

# Copy app, scripts, cron
COPY app/ /app/
COPY cron/ /app/cron/
COPY scripts/ /app/scripts/

# Install cron job
RUN chmod 644 /app/cron/2fa-cron \
    && crontab /app/cron/2fa-cron

# Create volumes
RUN mkdir -p /data /cron
VOLUME ["/data", "/cron"]

EXPOSE 8080

# Run cron in background and start FastAPI
CMD cron && uvicorn main:app --host 0.0.0.0 --port 8080
