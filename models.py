import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Visitor(db.Model):
    """Model for visitor tracking."""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=True)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_agent = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<Visitor {self.id}>'

class Conversion(db.Model):
    """Model for conversion tracking (successful OCR operations)."""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=True)
    conversion_date = db.Column(db.DateTime, default=datetime.utcnow)
    image_size = db.Column(db.Integer, nullable=True)
    language = db.Column(db.String(20), nullable=True)
    preprocessing_type = db.Column(db.String(20), nullable=True)
    characters_extracted = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Conversion {self.id}>'