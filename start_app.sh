#!/bin/bash
# Script to start the OCR application with Uvicorn
uvicorn ocr_app.api:app --host 0.0.0.0 --port 5000 --reload