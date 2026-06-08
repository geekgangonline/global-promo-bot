FROM python:3.9-slim

WORKDIR /app

# Install build dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Ensure stdout/stderr are unbuffered for Railway logs
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Expose if using webhook mode
EXPOSE 5000

# Run bot — webhook mode for Railway with health check
CMD python -c "
import os, sys
sys.stdout.write('Starting bot...\n')
sys.stdout.flush()
port = int(os.environ.get('PORT', 5000))
sys.stdout.write(f'PORT={port}\n')
sys.stdout.write(f'DEBUG={os.environ.get(\"DEBUG\")}\n')
sys.stdout.write(f'TOKEN exists: {bool(os.environ.get(\"TOKEN\"))}\n')
sys.stdout.flush()
from epush_bot import server
sys.stdout.write('Flask imported, starting server...\n')
sys.stdout.flush()
server.run(host='0.0.0.0', port=port)
"
