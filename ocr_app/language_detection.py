import logging
import numpy as np
import cv2

logger = logging.getLogger(__name__)

def detect_language(image):
    """
    Attempt to detect if the image contains Chinese or English text.
    This is a simple heuristic-based approach that examines character density patterns.
    
    Args:
        image: PIL Image object or a path to an image file
        
    Returns:
        String language code: 'chi_sim' for Chinese, 'eng' for English
    """
    try:
        # Convert PIL Image to OpenCV format if it's not a string path
        if isinstance(image, str):
            # Path to image
            cv_image = cv2.imread(image)
        else:
            # PIL Image object
            import numpy as np
            open_cv_image = np.array(image) 
            # Convert RGB to BGR (OpenCV uses BGR)
            cv_image = open_cv_image[:, :, ::-1].copy() 
            
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to create a binary image
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours in the binary image
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate metrics for language detection
        character_count = len(contours)
        aspect_ratios = []
        area_ratios = []
        
        for contour in contours:
            if cv2.contourArea(contour) > 20:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                if w > 0 and h > 0:
                    aspect_ratio = float(w) / h
                    area_ratio = cv2.contourArea(contour) / (w * h)
                    aspect_ratios.append(aspect_ratio)
                    area_ratios.append(area_ratio)
        
        # Calculate average metrics if there are enough contours
        if aspect_ratios:
            avg_aspect_ratio = sum(aspect_ratios) / len(aspect_ratios)
            avg_area_ratio = sum(area_ratios) / len(area_ratios)
            
            # Heuristic: Chinese characters tend to be more square-like with higher "fullness"
            if avg_aspect_ratio < 1.2 and avg_area_ratio > 0.5:
                logger.info(f"Detected likely Chinese text (ratio: {avg_aspect_ratio:.2f}, fullness: {avg_area_ratio:.2f})")
                return 'chi_sim'
                
        # Default to English if we can't identify Chinese characteristics
        logger.info("Defaulting to English language")
        return 'eng'
        
    except Exception as e:
        logger.error(f"Error in language detection: {str(e)}")
        # Fall back to English in case of error
        return 'eng'