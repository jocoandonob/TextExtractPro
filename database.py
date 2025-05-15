import os
from flask import Flask
from models import db

def init_db(app):
    """Initialize the database connection for the Flask app."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        database_url = "sqlite:///ocr_app.db"
        print(f"Warning: DATABASE_URL not found, using SQLite: {database_url}")
        
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize the app with the extension
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
    return db