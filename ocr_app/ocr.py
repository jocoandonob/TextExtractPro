import pytesseract
import logging
import tempfile
import subprocess
import os
import re
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Set Tesseract path based on environment variable or use the detected path
tesseract_cmd = os.environ.get("TESSERACT_CMD", "/nix/store/44vcjbcy1p2yhc974bcw250k2r5x5cpa-tesseract-5.3.4/bin/tesseract")
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def clean_text(text, fix_punctuation=True, fix_layout=True):
    """
    Clean up OCR text by fixing punctuation and layout issues.
    
    Args:
        text: The raw text from OCR
        fix_punctuation: Whether to fix common punctuation errors
        fix_layout: Whether to fix layout issues (sentence breaks, etc.)
        
    Returns:
        Cleaned text
    """
    if not text:
        return text
    
    # Fix the issue with dots converting to 1
    if fix_punctuation:
        # Replace standalone 1s that might be periods
        text = re.sub(r'(\s)1(\s)', r'\1.\2', text)
        # Fix other common OCR errors with punctuation
        text = text.replace(' ,', ',')
        text = text.replace(' .', '.')
        text = text.replace(' :', ':')
        text = text.replace(' ;', ';')
        text = text.replace(' !', '!')
        text = text.replace(' ?', '?')
    
    # Fix layout/alignment issues
    if fix_layout:
        # Join sentences that got broken across lines incorrectly
        # This is a simple version - more sophisticated NLP could be used
        lines = text.split('\n')
        new_lines = []
        current_line = ""
        
        for line in lines:
            line = line.strip()
            if not line:  # Keep empty lines
                if current_line:
                    new_lines.append(current_line)
                    current_line = ""
                new_lines.append("")
                continue
                
            # If current line ends with a sentence-ending punctuation, start a new line
            if current_line and (current_line.endswith('.') or 
                               current_line.endswith('!') or 
                               current_line.endswith('?') or
                               current_line.endswith('。')):  # Chinese period
                new_lines.append(current_line)
                current_line = line
            elif not current_line:  # Start a new paragraph
                current_line = line
            else:  # Continue the sentence
                current_line += " " + line
        
        # Add the last line if there's anything left
        if current_line:
            new_lines.append(current_line)
            
        text = '\n'.join(new_lines)
    
    return text


def extract_text(image, language="eng"):
    """
    Extract text from an image using Tesseract OCR.
    
    Args:
        image: PIL Image object
        language: Language code for OCR (default: 'eng', also supports 'chi_sim', 'chi_tra', etc.)
        
    Returns:
        Extracted text as string
    """
    try:
        logger.info("Starting OCR text extraction")
        
        # Verify we have a valid image
        if image is None:
            raise ValueError("Image is None - cannot perform OCR")
            
        if not isinstance(image, Image.Image):
            raise TypeError(f"Expected PIL.Image, got {type(image)}")
        
        # Create a temporary directory for OCR files
        temp_dir = tempfile.mkdtemp(prefix="ocr_")
        temp_path = os.path.join(temp_dir, "ocr_image.png")
        output_base = os.path.join(temp_dir, "ocr_output")
        output_file = output_base + ".txt"
        
        try:
            # Save the image to the temporary file
            image.save(temp_path)
            logger.info(f"Saved temporary image for OCR to {temp_path}")
            
            # Log image details
            width, height = image.size
            format_info = f"{image.format}" if image.format else "Unknown"
            logger.info(f"Image info: {width}x{height} {format_info} {image.mode}")
            
            # Configure Tesseract options based on language
            # common PSM modes:
            # 3 = Fully automatic page segmentation, but no OSD (default)
            # 6 = Assume a single uniform block of text
            # 11 = Sparse text - Find as much text as possible in no particular order
            # 
            # For Chinese/Japanese text, PSM 6 or 11 often works better
            psm_mode = 6
            if language in ["chi_sim", "chi_tra", "jpn", "kor"]:
                # For Asian languages, try different PSM mode for better results
                psm_mode = 11
                
            custom_config = f'--oem 3 --psm {psm_mode}'
            
            logger.info(f"Using language: {language} with config: {custom_config}")
            
            # Run OCR in two ways to ensure we get a result
            
            # Method 1: Use pytesseract directly with language
            logger.info(f"Running pytesseract with language: {language}")
            text = pytesseract.image_to_string(image, lang=language, config=custom_config)
            
            # If the result is empty, try direct command line for more debug info
            if not text.strip():
                logger.warning(f"No text returned from pytesseract with {language}, trying direct command")
                
                # Method 2: Use command line directly for better debug output
                cmd = [tesseract_cmd, temp_path, output_base, "-l", language, f"--psm", str(psm_mode)]
                
                proc = subprocess.run(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                logger.info(f"Tesseract exit code: {proc.returncode}")
                if proc.stdout:
                    logger.info(f"Tesseract stdout: {proc.stdout}")
                if proc.stderr:
                    logger.warning(f"Tesseract stderr: {proc.stderr}")
                
                # Read text from output file if it exists
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        text = f.read()
                        logger.info(f"Read {len(text)} characters from direct command output")
                else:
                    logger.warning(f"Output file not found: {output_file}")
        
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                if os.path.exists(output_file):
                    os.unlink(output_file)
                # Try to remove temp directory
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"Error cleaning up temp files: {e}")
        
        # Basic cleaning
        text = text.strip()
        
        if not text:
            logger.warning("No text was extracted from the image")
            return "No text detected in the image. Try a different preprocessing method or ensure the image contains text."
        
        # Apply our advanced text cleaning (but don't apply layout fixes by default)
        # Layout fixes will be optional via API/button
        text = clean_text(text, fix_punctuation=True, fix_layout=False)
        
        logger.info(f"Successfully extracted {len(text)} characters of text")
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text with OCR: {str(e)}", exc_info=True)
        return f"OCR processing error: {str(e)}. Please try again with a different image or preprocessing method."

def get_ocr_info():
    """Get information about the Tesseract OCR installation."""
    try:
        # Run tesseract version command directly
        result = subprocess.run(
            [tesseract_cmd, "--version"], 
            capture_output=True, 
            text=True,
            check=False
        )
        
        version_info = result.stdout.strip() if result.stdout else "Unknown"
        
        return {
            "tesseract_version": pytesseract.get_tesseract_version(),
            "tesseract_path": pytesseract.pytesseract.tesseract_cmd,
            "version_details": version_info
        }
    except Exception as e:
        logger.error(f"Error getting OCR info: {str(e)}", exc_info=True)
        return {
            "tesseract_version": "Unknown",
            "tesseract_path": pytesseract.pytesseract.tesseract_cmd,
            "error": str(e)
        }
