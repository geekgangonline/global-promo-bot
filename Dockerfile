FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Expose if using webhook mode
EXPOSE 5000

# Run bot in polling mode
CMD ["python", "epush_bot.py"]
