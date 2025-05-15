import os
import logging
import time
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
import shutil
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_processor import preprocess_image
from .ocr import extract_text, clean_text
from .tracking import track_visitor, track_conversion, get_statistics

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OCR Application",
    description="An application for extracting text from images using Tesseract OCR",
    version="1.0.0",
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Create temporary directory for storing uploaded images
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# Define valid image extensions
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page of the application."""
    # Track visitor
    try:
        track_visitor(request)
    except Exception as e:
        logger.error(f"Error tracking visitor: {str(e)}")
    
    # Get statistics for the footer
    stats = get_statistics()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats
    })

@app.post("/upload/")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    preprocess_type: str = Form("default"),
    language: str = Form("eng")
):
    """
    Upload an image and extract text using OCR.
    
    Args:
        request: The HTTP request
        file: The image file to extract text from
        preprocess_type: Type of preprocessing to apply (default, grayscale, threshold, adaptive)
        language: Language for OCR (eng, chi_sim)
    
    Returns:
        JSON response with extracted text and processed image path
    """
    start_time = time.time()
    
    try:
        # Validate file extension
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
            
        # We already checked that filename is not None
        filename: str = file.filename  # Type hint to help LSP
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension not in VALID_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Supported formats: {', '.join(VALID_EXTENSIONS)}"
            )
        
        # Generate a unique filename for the upload
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        temp_path = TEMP_DIR / unique_filename
        
        # Save the uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate language
        if language not in ["eng", "chi_sim"]:
            language = "eng"  # Default to English if invalid language
        
        logger.info(f"Processing image with language: {language}, preprocessing: {preprocess_type}")
        
        # Preprocess the image
        processed_image = preprocess_image(str(temp_path), preprocess_type)
        
        # Extract text using OCR with the specified language
        text = extract_text(processed_image, language)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Track this successful conversion
        try:
            char_count = len(text) if text else 0
            track_conversion(
                request, 
                file.size, 
                language, 
                preprocess_type,
                char_count
            )
        except Exception as e:
            logger.error(f"Error tracking conversion: {str(e)}")
        
        # Clean up temporary file
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception as e:
            logger.warning(f"Error cleaning up temp file: {e}")
        
        # Return the extracted text and processing information
        return {
            "filename": file.filename,
            "size": file.size,
            "text": text,
            "processing_time": round(processing_time, 2),
            "preprocessing_type": preprocess_type,
            "language": language
        }
    
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        # Clean up temporary file in case of error
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception as cleanup_error:
            logger.warning(f"Error cleaning up temp file after error: {cleanup_error}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/api/extract-text/")
async def extract_text_api(
    request: Request,
    file: UploadFile = File(...),
    preprocess_type: str = Form("default"),
    language: str = Form("eng")
):
    """
    API endpoint to extract text from an image.
    
    Args:
        request: The HTTP request
        file: The image file to extract text from
        preprocess_type: Type of preprocessing to apply (default, grayscale, threshold, adaptive)
        language: Language for OCR (eng, chi_sim)
    
    Returns:
        JSON response with extracted text
    """
    return await upload_image(
        request=request, 
        file=file, 
        preprocess_type=preprocess_type, 
        language=language
    )
    
@app.get("/api/statistics/")
async def get_usage_statistics():
    """
    Get usage statistics for the OCR application.
    
    Returns:
        JSON response with usage statistics
    """
    try:
        stats = get_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return {
            "success": False,
            "error": f"Error getting statistics: {str(e)}"
        }

@app.get("/api/preprocessing-types/")
async def get_preprocessing_types():
    """Get available preprocessing types."""
    return {
        "preprocessing_types": [
            {"id": "default", "name": "Default"},
            {"id": "grayscale", "name": "Grayscale"},
            {"id": "threshold", "name": "Binary Threshold"},
            {"id": "adaptive", "name": "Adaptive Threshold"},
            {"id": "denoise", "name": "Denoise"}
        ]
    }

@app.get("/api/languages/")
async def get_languages():
    """Get available OCR languages."""
    return {
        "languages": [
            {"id": "eng", "name": "English"},
            {"id": "chi_sim", "name": "Chinese (Simplified)"}
        ]
    }
    
@app.post("/api/detect-language/")
async def detect_image_language(file: UploadFile = File(...)):
    """
    Detect the language in an uploaded image.
    
    Args:
        file: The image file to analyze
        
    Returns:
        JSON response with detected language
    """
    try:
        # Validate file existence
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
            
        # Validate file extension
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower() if filename else ""
        if file_extension not in VALID_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {', '.join(VALID_EXTENSIONS)}"
            )
            
        # Generate a unique filename for the upload
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        temp_path = TEMP_DIR / unique_filename
        
        # Save the uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Detect language using our detection function
        detected_language = detect_language(str(temp_path))
        
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except Exception as e:
            logger.warning(f"Error removing temp file: {e}")
            
        return {
            "success": True,
            "language": detected_language,
            "filename": file.filename
        }
    
    except Exception as e:
        logger.error(f"Error detecting language: {str(e)}")
        return {
            "success": False,
            "error": f"Error processing image: {str(e)}",
            "language": "eng"  # Default to English on error
        }
    
@app.post("/api/clean-text/")
async def clean_text_api(text: str = Form(...), fix_layout: bool = Form(True)):
    """
    Clean the OCR text by fixing punctuation and formatting issues.
    
    Args:
        text: The text to clean
        fix_layout: Whether to fix layout/alignment issues
        
    Returns:
        Cleaned text
    """
    try:
        if not text:
            return {"success": False, "error": "No text provided"}
            
        # Apply text cleaning
        cleaned_text = clean_text(text, fix_punctuation=True, fix_layout=fix_layout)
        
        return {
            "success": True,
            "original_text": text,
            "cleaned_text": cleaned_text
        }
    except Exception as e:
        logger.error(f"Error cleaning text: {str(e)}")
        return {"success": False, "error": f"Error processing text: {str(e)}"}

@app.on_event("startup")
async def startup_event():
    logger.info("OCR Application starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("OCR Application shutting down")
    # Clean up temporary files
    if TEMP_DIR.exists():
        for file in TEMP_DIR.glob("*"):
            try:
                file.unlink()
            except Exception as e:
                logger.error(f"Error deleting temporary file {file}: {e}")
