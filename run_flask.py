"""
Simple script to run the OCR application using Flask
This script provides a wrapper around our FastAPI application
"""

from main import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)