FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Disable Python bytecode and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set HF_HOME so models are downloaded to a predictable location inside the container
ENV HF_HOME=/app/data/hf_cache

# Create required runtime directories
RUN mkdir -p /app/data/hf_cache /app/logs

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start using uvicorn with explicit reverse proxy support
CMD ["sh", "-c", "uvicorn app.core.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
