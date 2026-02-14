#!/bin/bash
# Start Streamlit frontend

echo "Starting PDF Chatbot Frontend..."
echo "================================"

# Activate virtual environment
source venv/Scripts/activate

# Install frontend dependencies if needed
pip install -r frontend/requirements.txt -q

# Start Streamlit
streamlit run frontend/streamlit_app.py --server.port 8501
