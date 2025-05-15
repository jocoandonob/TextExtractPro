# TextExtractPro

TextExtractPro is a powerful OCR (Optical Character Recognition) application that combines Flask and FastAPI to provide a robust text extraction service. The application allows users to extract text from images and documents efficiently.

## Features

- OCR processing for various image formats
- RESTful API endpoints using FastAPI
- Flask wrapper for enhanced functionality
- Database integration for storing results
- Easy deployment with multiple server options

## Tech Stack

- Python
- Flask (Web framework for proxy and main application)
- FastAPI (API framework)
- Uvicorn (ASGI server)
- SQLAlchemy (Database ORM)
- Other dependencies specified in `pyproject.toml`

## Project Structure

```
TextExtractPro/
├── ocr_app/           # Main OCR application package
├── static/            # Static files
├── templates/         # HTML templates
├── main.py           # Flask application wrapper
├── database.py       # Database configuration
├── models.py         # Database models
├── pyproject.toml    # Project dependencies
└── various .sh files # Server startup scripts
```

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd TextExtractPro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

You have several options to run the application:

1. Using Flask development server:
```bash
python run_flask.py
```

2. Using the start scripts:
```bash
# Using Flask
./start_app.sh

# Using Uvicorn directly
./start_uvicorn.sh

# Using custom workflow
./custom_workflow.sh
```

The application will start on port 5000 (Flask) and the FastAPI service will run on port 8000.

## API Endpoints

The application provides various API endpoints through FastAPI. Access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuration

The application can be configured through environment variables:
- `FLASK_SECRET_KEY`: Secret key for Flask application (default: 'dev_key_for_ocr_app')
- Additional configuration can be set in the respective configuration files

## Development

To contribute to the project:

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

[Your License Here]

## Support

For support, please [create an issue](your-repository-url/issues) in the repository. 