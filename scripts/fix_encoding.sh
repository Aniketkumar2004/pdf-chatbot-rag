#!/bin/bash
echo "Fixing encoding issues..."

# 1. Stop any running processes
echo "1. Cleaning up old data..."
rm -rf data/chroma_db
mkdir -p data/chroma_db

echo "2. Files updated"
echo "3. Ready to restart"
echo ""
echo "Now run:"
echo "  python -m uvicorn app.main:app --reload"
echo ""
echo "Then in another terminal:"
echo "  streamlit run frontend/streamlit_app.py"
