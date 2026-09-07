# VeriGuard AI - Hardened Enterprise Multi-Stage Dockerfile
# Base Image: Official Debian-Slim with Python 3.13
FROM python:3.13-slim-bookworm AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Install system dependencies: Tesseract OCR (v5) with English & Hindi models, OpenCV & GL dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    libgl1 \
    libglib2.0-0 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Create non-root enterprise system user
RUN groupadd -g 1001 veriguard && \
    useradd -u 1001 -g veriguard -m -s /bin/bash veriguard

# Copy backend requirements and install dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pyjwt cryptography python-pptx

# Copy application source code
COPY backend /app/backend
COPY tesseract_config.py /app/tesseract_config.py

# Create ephemeral temporary scratch directory with strict permissions
RUN mkdir -p /app/temp && \
    chown -R veriguard:veriguard /app

# Switch to non-root user for least-privilege security
USER veriguard

# Expose backend REST API port
EXPOSE 8000

# Docker Healthcheck targeting FastAPI /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

# Launch FastAPI ASGI server via Uvicorn
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
