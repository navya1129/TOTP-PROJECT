# ------------ Stage 1: Build environment --------------
FROM python:3.10-slim AS builder

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --user -r requirements.txt

# ------------ Stage 2: Runtime image -------------------
FROM python:3.10-slim

WORKDIR /app

# Install cron
RUN apt-get update && apt-get install -y cron && apt-get clean

# Copy installed Python packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY app/ /app/

# Copy scripts
COPY scripts/ /scripts/

# DO NOT RUN crontab here

# Start cron + keep alive
CMD ["sh", "-c", "cron && tail -f /dev/null"]
