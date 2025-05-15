import cv2
import numpy as np
import logging
import os
import tempfile
from PIL import Image, ImageEnhance, ImageFilter
import io

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def load_image(image_path):
    """
    Load an image from a file path.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        OpenCV image (numpy array)
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # First try PIL loading to check if image is valid
        try:
            pil_image = Image.open(image_path)
            pil_image.verify()  # Verify it's a valid image
            logger.info(f"Verified image with PIL: {image_path}, format: {pil_image.format}")
        except Exception as e:
            logger.warning(f"PIL image verification failed: {e}")
        
        # Load image using OpenCV
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Failed to load image from {image_path} with OpenCV")
        
        # Log image information
        height, width, channels = image.shape if len(image.shape) == 3 else (*image.shape, 1)
        logger.info(f"Loaded image: {image_path}, dimensions: {width}x{height}, channels: {channels}")
        
        return image
        
    except Exception as e:
        logger.error(f"Error loading image: {str(e)}", exc_info=True)
        raise

def preprocess_image(image_path, preprocessing_type="default"):
    """
    Preprocess an image for OCR.
    
    Args:
        image_path: Path to the image file
        preprocessing_type: Type of preprocessing to apply
        
    Returns:
        PIL Image object ready for OCR
    """
    try:
        logger.info(f"Preprocessing image with method: {preprocessing_type}")
        
        # Load the image with OpenCV
        cv_image = load_image(image_path)
        
        # Resize image if it's too large (to improve processing time)
        max_dimension = 2000
        height, width = cv_image.shape[:2]
        
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            cv_image = cv2.resize(cv_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            logger.info(f"Resized image to: {new_width}x{new_height}")
        
        # Save intermediate results for debugging
        debug_dir = os.path.join(tempfile.gettempdir(), "ocr_debug")
        os.makedirs(debug_dir, exist_ok=True)
        
        # Apply preprocessing based on type
        if preprocessing_type == "grayscale":
            # Convert to grayscale
            processed = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(os.path.join(debug_dir, "grayscale.png"), processed)
        
        elif preprocessing_type == "threshold":
            # Convert to grayscale and apply binary threshold
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            # Apply Otsu's thresholding
            processed = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            cv2.imwrite(os.path.join(debug_dir, "threshold.png"), processed)
        
        elif preprocessing_type == "adaptive":
            # Convert to grayscale and apply adaptive threshold
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            # Apply adaptive thresholding
            processed = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            cv2.imwrite(os.path.join(debug_dir, "adaptive.png"), processed)
        
        elif preprocessing_type == "denoise":
            # Convert to grayscale and denoise
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            # Apply non-local means denoising
            processed = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            cv2.imwrite(os.path.join(debug_dir, "denoise.png"), processed)
        
        else:  # default
            # Convert BGR to RGB
            processed = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(os.path.join(debug_dir, "default.png"), cv2.cvtColor(processed, cv2.COLOR_RGB2BGR))
        
        # Convert OpenCV image to PIL Image for Tesseract
        if len(processed.shape) == 2:  # Grayscale
            pil_image = Image.fromarray(processed)
        else:  # RGB
            pil_image = Image.fromarray(processed)
        
        # Additional PIL-based enhancements for better OCR
        if preprocessing_type == "default":
            # Increase contrast slightly
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.5)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.5)
        
        # Save the final PIL image for reference
        pil_debug_path = os.path.join(debug_dir, f"final_{preprocessing_type}.png")
        pil_image.save(pil_debug_path)
        logger.info(f"Saved processed image to: {pil_debug_path}")
        
        logger.info(f"Image preprocessing completed: {preprocessing_type}")
        return pil_image
    
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}", exc_info=True)
        # Return a blank image with an error message
        error_image = Image.new('RGB', (800, 100), color=(0, 0, 0))
        logger.error("Returning blank image due to preprocessing error")
        return error_image
