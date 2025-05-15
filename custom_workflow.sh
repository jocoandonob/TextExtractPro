#!/bin/bash
# Custom workflow script for running the OCR application
echo "Starting OCR Application with Uvicorn..."
# Kill any existing uvicorn processes
pkill -f uvicorn || true
# Start the application
cd /home/runner/workspace 
exec uvicorn asgi:application --host 0.0.0.0 --port 5000