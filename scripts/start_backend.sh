#!/bin/bash
# Start FastAPI backend

echo "Starting PDF Chatbot Backend..."
echo "================================"

# Activate virtual environment
source venv/Scripts/activate

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
