# FastAPI Backend with Docker

A modern REST API backend built with FastAPI and Docker.

## Features

- FastAPI framework with automatic API documentation
- Docker support for easy deployment
- CRUD operations for items
- Pydantic models for request/response validation
- Hot reload for development

## API Endpoints

- `GET /`: Welcome message
- `GET /items`: List all items
- `GET /items/{item_id}`: Get a specific item
- `POST /items`: Create a new item
- `PUT /items/{item_id}`: Update an existing item
- `DELETE /items/{item_id}`: Delete an item

## Setup and Running

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
cd app
uvicorn main:app --reload
```

### Docker

1. Build the Docker image:
```bash
docker build -t fastapi-backend .
```

2. Run the container:
```bash
docker run -p 8000:8000 fastapi-backend
```

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 