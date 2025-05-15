"""
ASGI adapter for Gunicorn to work with FastAPI.
This file is a compatibility layer that allows Gunicorn to serve FastAPI applications.
"""

from ocr_app.api import app
import uvicorn.workers

# Create a custom worker class for Gunicorn
class ASGIWorker(uvicorn.workers.UvicornWorker):
    """Custom Uvicorn worker for Gunicorn that handles ASGI applications."""
    CONFIG_KWARGS = {
        "loop": "auto",
        "http": "auto",
    }