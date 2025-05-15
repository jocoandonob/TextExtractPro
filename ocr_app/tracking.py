import os
import logging
from datetime import datetime
from models import db, Visitor, Conversion

logger = logging.getLogger(__name__)

def track_visitor(request):
    """
    Track a visitor to the application.
    
    Args:
        request: The incoming request
    """
    try:
        # Get IP address and user agent from the request
        ip_address = request.client.host
        user_agent = request.headers.get('user-agent', 'Unknown')
        
        # Create a new visitor record
        visitor = Visitor()
        visitor.ip_address = ip_address
        visitor.user_agent = user_agent
        visitor.visit_date = datetime.utcnow()
        
        # Add to the database
        db.session.add(visitor)
        db.session.commit()
        
        return True
    except Exception as e:
        logger.error(f"Error tracking visitor: {str(e)}")
        return False

def track_conversion(request, image_size, language, preprocessing_type, characters_extracted):
    """
    Track a successful OCR conversion.
    
    Args:
        request: The incoming request
        image_size: Size of the processed image
        language: OCR language used
        preprocessing_type: Preprocessing method used
        characters_extracted: Number of characters extracted
    """
    try:
        # Get IP address from the request
        ip_address = request.client.host
        
        # Create a new conversion record
        conversion = Conversion()
        conversion.ip_address = ip_address
        conversion.image_size = image_size
        conversion.language = language
        conversion.preprocessing_type = preprocessing_type
        conversion.characters_extracted = characters_extracted
        conversion.conversion_date = datetime.utcnow()
        
        # Add to the database
        db.session.add(conversion)
        db.session.commit()
        
        return True
    except Exception as e:
        logger.error(f"Error tracking conversion: {str(e)}")
        return False

def get_statistics():
    """
    Get visitor and conversion statistics.
    
    Returns:
        Dictionary with statistics
    """
    try:
        visitor_count = db.session.query(Visitor).count()
        conversion_count = db.session.query(Conversion).count()
        
        # Get statistics by language
        language_stats = db.session.query(
            Conversion.language, 
            db.func.count(Conversion.id)
        ).group_by(Conversion.language).all()
        
        # Get statistics by preprocessing type
        preprocessing_stats = db.session.query(
            Conversion.preprocessing_type, 
            db.func.count(Conversion.id)
        ).group_by(Conversion.preprocessing_type).all()
        
        # Calculate conversion rate
        conversion_rate = 0
        if visitor_count > 0:
            conversion_rate = (conversion_count / visitor_count) * 100
            
        # Format language stats
        language_data = {lang: count for lang, count in language_stats}
        
        # Format preprocessing stats
        preprocessing_data = {prep: count for prep, count in preprocessing_stats}
        
        return {
            "visitor_count": visitor_count,
            "conversion_count": conversion_count,
            "conversion_rate": round(conversion_rate, 2),
            "language_stats": language_data,
            "preprocessing_stats": preprocessing_data
        }
    except Exception as e:
        print(f"Error getting statistics: {str(e)}")
        return {
            "visitor_count": 0,
            "conversion_count": 0,
            "conversion_rate": 0,
            "language_stats": {},
            "preprocessing_stats": {}
        }