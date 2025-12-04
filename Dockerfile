# -------- Stage 1: Builder --------
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements and install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------- Stage 2: Runtime --------
FROM python:3.11-slim

WORKDIR /app

# Install cron and timezone tools
RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/* \
 && ln -fs /usr/share/zoneinfo/UTC /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata

# Copy dependencies from builder
COPY --from=builder /usr/local /usr/local

# Copy app, scripts, and cron
COPY app/ /app/
COPY scripts/ /app/scripts/
COPY cron/ /app/cron/  # Make sure this folder exists on host

# Set up cron job
RUN chmod 644 /app/cron/2fa-cron \
 && crontab /app/cron/2fa-cron

# Create volumes for persistent data
RUN mkdir -p /data /cron
VOLUME ["/data", "/cron"]

EXPOSE 8080

# Start cron in background and FastAPI
CMD cron && uvicorn main:app --host 0.0.0.0 --port 8080
