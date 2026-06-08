FROM python:3.9-slim

WORKDIR /app

# Install build dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Ensure stdout/stderr are unbuffered for Railway logs
ENV PYTHONUNBUFFERED=1

# Copy bot code
COPY . .

RUN chmod +x entrypoint.sh

# Expose if using webhook mode
EXPOSE 5000

# Run bot
CMD ["./entrypoint.sh"]
