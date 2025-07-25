# Adobe Hackathon Round 1A - Dockerfile
# Optimized for AMD64, CPU-only, offline execution

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY pdf_parser.py .
COPY heading_extractor.py .
COPY utils.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set permissions
RUN chmod +x main.py

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Labels for documentation
LABEL version="1.0"
LABEL description="Adobe Hackathon Round 1A - Document Outline Extraction"
LABEL maintainer="hackathon-team"

# Network disabled by default (--network none in docker run)
# Volume mounts: /app/input and /app/output