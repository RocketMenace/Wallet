#!/bin/bash

# Exit on any error
set -e

echo "Waiting for database..."
sleep 5

# Run Alembic migrations (optional - only if you still want migrations)
echo "Running database migrations..."
alembic upgrade head

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --loop uvloop --http httptools