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
- Tesseract OCR (OCR engine)
- Other dependencies specified in `pyproject.toml`

## Prerequisites

### 1. Install Tesseract OCR

#### Windows:
1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and note the installation path
3. Add Tesseract to your system PATH:
   - Search for "Environment Variables" in Windows
   - Edit the PATH variable
   - Add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`)

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

#### macOS:
```bash
brew install tesseract
```

### 2. Verify Installation
```bash
tesseract --version
```

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

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (optional):
```bash
# Windows
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Linux/macOS
export TESSERACT_CMD=/usr/bin/tesseract
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
- `TESSERACT_CMD`: Path to Tesseract executable (if not in system PATH)
- Additional configuration can be set in the respective configuration files

## Troubleshooting

### Common Issues

1. **Tesseract Not Found Error**
   - Verify Tesseract is installed: `tesseract --version`
   - Check if Tesseract is in your PATH
   - Set the `TESSERACT_CMD` environment variable to the full path of the Tesseract executable

2. **OCR Quality Issues**
   - Ensure input images are clear and well-lit
   - Try preprocessing images before OCR
   - Consider using different Tesseract language packs for non-English text

## Development

To contribute to the project:

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

[Your License Here]

## Support

For support, please [create an issue](your-repository-url/issues) in the repository. 