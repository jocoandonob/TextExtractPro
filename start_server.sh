#!/bin/bash
# Start server using gunicorn with uvicorn workers for FastAPI
gunicorn -w 1 -k uvicorn.workers.UvicornWorker ocr_app.api:app --bind 0.0.0.0:5000 --reload