FROM python:3.10-slim AS builder
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.10-slim
WORKDIR /app

# Install cron
RUN apt-get update && apt-get install -y cron && apt-get clean

# Copy installed packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy python app
COPY app/ /app/
COPY scripts/ /scripts/

# Set permissions for cron job (cron REQUIRES 0644)
RUN chmod 0644 /etc/cron.d/2fa-cron || true

# Register cron job
RUN crontab /etc/cron.d/2fa-cron

# Start cron + keep container running
CMD ["sh", "-c", "cron -f"]
