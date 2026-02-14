#!/bin/bash
# Start both backend and frontend

echo "Starting PDF Chatbot (Backend + Frontend)..."
echo "============================================="

# Function to cleanup on exit
cleanup() {
    echo "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Activate virtual environment
source venv/Scripts/activate

# Start backend in background
echo "Starting backend on http://localhost:8000"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in background
echo "Starting frontend on http://localhost:8501"
streamlit run frontend/streamlit_app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "============================================="
echo "✅ Services started!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:8501"
echo "   API Docs: http://localhost:8000/docs"
echo "============================================="
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait
