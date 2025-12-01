# Dockerfile for Honeytoken Detection System
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY honeytoken_generator.py .
COPY token_scanner.py .
COPY github_integration.py .
COPY alert_system.py .
COPY webhook_server.py .
COPY honeytoken_injector.py .
COPY ci_scanner.py .
COPY setup_script.py .
COPY test_suite.py .
COPY dashboard.html .

# Create data directories
RUN mkdir -p /app/data /app/logs /app/reports

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Expose webhook server port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Default command (can be overridden)
CMD ["python", "webhook_server.py"]
