#!/bin/bash
# Start server using pure uvicorn
uvicorn asgi:application --host 0.0.0.0 --port 5000