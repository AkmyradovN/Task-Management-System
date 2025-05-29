# Task-Management-System

A simple task management system built with FastAPI that handles background processing. Uses PostgreSQL for storage and includes comprehensive testing.

## Features

- Create, read, update, and delete tasks
- Simulate background task processing
- Filter and paginate task lists
- Automatic task status logging
- Database migrations support
- Full Docker containerization
- Complete test coverage

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose

### Running with Docker (Recommended)
```bash
git clone https://github.com/AkmyradovN/Task-Management-System.git
cd Task-Management-System
docker-compose up --build

Access these after startup:

    API: http://localhost:8000

    Interactive docs: http://localhost:8000/docs

    Alternative docs: http://localhost:8000/redoc

Running Locally

    Install dependencies:

bash

pip install -e .

    Start PostgreSQL:

bash

docker run --name postgres-taskdb \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=taskdb \
  -p 5432:5432 \
  -d postgres:15

    Set environment variable:

bash

export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/taskdb"

    Apply database migrations:

bash

alembic upgrade head

    Start the server:

bash

uvicorn app.main:app --reload