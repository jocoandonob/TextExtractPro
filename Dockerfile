# Use Python 3.11 as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    # Install required language packs
    tesseract-ocr-eng \
    tesseract-ocr-chi-sim \
    # Additional dependencies for OpenCV
    libgl1-mesa-glx \
    libglib2.0-0 \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set Tesseract environment variables
ENV TESSERACT_CMD=/usr/bin/tesseract \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Expose ports for Flask and FastAPI
EXPOSE 5000 8000

# Create a script to run both servers
RUN echo '#!/bin/bash\n\
uvicorn ocr_app.api:app --host 0.0.0.0 --port 8000 & \n\
gunicorn --bind 0.0.0.0:5000 main:app\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Set the entrypoint
CMD ["/app/start.sh"] 