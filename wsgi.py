"""
WSGI entry point for Gunicorn.
This file serves as the entry point for Gunicorn to run our Flask application.
"""
from main import app

# This variable is used by Gunicorn to find the application
application = app