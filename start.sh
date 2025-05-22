#!/bin/bash
uvicorn ocr_app.api:app --host 0.0.0.0 --port 8000 &
gunicorn --bind 0.0.0.0:5000 main:app
wait 