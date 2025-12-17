#!/bin/bash
# Development startup script for SubScout backend

set -e

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Load environment variables
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if PostgreSQL and Redis are available (optional for basic testing)
echo "Starting SubScout API server..."
echo "Note: Ensure PostgreSQL and Redis are running for full functionality"
echo "API will be available at: http://localhost:8000"
echo "API docs will be available at: http://localhost:8000/docs"
echo ""

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

