# Use Python 3.11 as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TESSERACT_CMD=/usr/bin/tesseract \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Install system dependencies and clean up in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg2 \
    curl \
    software-properties-common \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-eng \
    tesseract-ocr-chi-sim \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Verify Tesseract installation
    tesseract --version && \
    tesseract --list-langs && \
    ls -l /usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata

# Set the working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/temp /app/static /app/templates

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a non-root user and set permissions
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod +x /app/start.sh

# Switch to non-root user
USER appuser

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose ports for Flask and FastAPI
EXPOSE 5000 8000

# Set the entrypoint
ENTRYPOINT ["/app/start.sh"] 