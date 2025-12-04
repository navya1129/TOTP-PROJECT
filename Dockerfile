# ------------ Stage 1: Build the Python environment --------------
FROM python:3.10-slim AS builder

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --user -r requirements.txt


# ------------ Stage 2: Final Runtime Image ------------------------
FROM python:3.10-slim

WORKDIR /app

# Copy installed Python packages
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

# Copy application files
COPY app/ /app/

# Copy scripts
COPY scripts/ /scripts/

# Copy cron job
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Apply correct permissions for cron
RUN chmod 0644 /etc/cron.d/2fa-cron

# Enable the cron job
RUN crontab /etc/cron.d/2fa-cron

# Create logs directory
RUN mkdir -p /logs

# Start cron + main app
CMD cron && python3 main.py
