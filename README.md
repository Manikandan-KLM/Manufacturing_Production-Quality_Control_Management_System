# Manufacturing Production & Quality Control Management System

## Project Description

This project is a backend application developed using FastAPI to manage manufacturing production, inventory, machine maintenance, and quality control processes.

## Technologies Used

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic
* JWT Authentication
* Alembic
* Pytest
* Redis
* Celery
* Docker

## Features

* User Authentication and Role-Based Access Control
* Product and Material Management
* Production Order and Batch Management
* Inventory Management
* Machine Maintenance
* Quality Inspection and Defect Tracking
* Dashboard and Reports
* Email Notifications
* Redis Caching
* WebSocket-Based Production Monitoring
* CSV and Excel Export
* QR Code and Barcode Batch Tracking
* API Rate Limiting
* Health Check and Prometheus Metrics

## Installation

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd Manufacturing_System
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file and configure the database URL, JWT secret, Redis URL, and other required settings.

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

## API Documentation

After starting the application, open:

* Swagger UI: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc
* Health Check: http://127.0.0.1:8000/health

## Run Tests

```bash
pytest -v
```

## Docker

Start the application using Docker Compose:

```bash
docker compose up --build -d
```

## Project Objective

The objective of this project is to simplify manufacturing operations by managing production, inventory, machines, and quality control through a REST API.

## Author

Manikandan
