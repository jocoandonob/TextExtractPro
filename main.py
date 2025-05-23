"""
OCR Application - FastAPI implementation
"""
import os
import logging
import uvicorn
from ocr_app.api import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Start the FastAPI application
    logger.info(f"Starting OCR Application on port {port}")
    uvicorn.run(
        "ocr_app.api:app",
        host="0.0.0.0",
        port=port,
        reload=True
    ) 