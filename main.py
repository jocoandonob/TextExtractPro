"""
OCR Application - Flask wrapper for FastAPI
"""
import os
import sys
import subprocess
import threading
import time
import logging
import atexit
from flask import Flask, request, Response, redirect
from database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev_key_for_ocr_app')

# Initialize the database
db = init_db(app)
uvicorn_process = None

def start_uvicorn():
    """Start the FastAPI application with Uvicorn in a subprocess"""
    global uvicorn_process
    # Start Uvicorn as a subprocess
    cmd = ["uvicorn", "ocr_app.api:app", "--host", "0.0.0.0", "--port", "8000"]
    uvicorn_process = subprocess.Popen(cmd)
    
    # Wait for Uvicorn to start
    time.sleep(2)
    logger.info("OCR Application: Uvicorn started on port 8000")

def stop_uvicorn():
    """Stop the Uvicorn subprocess"""
    global uvicorn_process
    if uvicorn_process:
        logger.info("OCR Application: Stopping Uvicorn")
        uvicorn_process.terminate()
        uvicorn_process.wait()

# Register cleanup function
atexit.register(stop_uvicorn)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    """Proxy all requests to the FastAPI app"""
    import requests
    
    # Check if uvicorn is running, start if needed
    if uvicorn_process is None or uvicorn_process.poll() is not None:
        start_uvicorn()
    
    # Determine the FastAPI url
    url = f'http://localhost:8000/{path}'
    
    try:
        # Forward the request
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
            timeout=30
        )
        
        # Create the response
        response = Response(resp.raw.read(), resp.status_code)
        
        # Add headers
        for key, value in resp.headers.items():
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                response.headers[key] = value
                
        return response
    
    except requests.exceptions.RequestException as e:
        logger.error(f"OCR Application: Proxy error - {str(e)}")
        return Response(f"Error connecting to OCR service: {str(e)}", status=500)

# Start Uvicorn when this module is imported
threading.Thread(target=start_uvicorn, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
