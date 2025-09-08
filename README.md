# FastAPI Template

A simple template for building APIs with FastAPI, a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.

## Features

- FastAPI for high-performance API development
- Automatic interactive API documentation with Swagger UI
- Built-in support for async operations
- Easy integration with databases (e.g., SQLAlchemy)
- Pydantic for data validation
- CORS support for cross-origin requests

## Installation

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

## Usage

1. Run the development server:

   ```bash
   uvicorn src.app:app --reload
   ```

2. Open your browser and navigate to `http://127.0.0.1:8000/docs` for interactive API documentation.
