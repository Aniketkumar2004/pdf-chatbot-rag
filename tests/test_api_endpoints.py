"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path
import io

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "PDF Chatbot" in data["message"]

@pytest.mark.skipif(not Path("tests/sample.pdf").exists(), reason="Sample PDF not found")
def test_upload_endpoint():
    """Test PDF upload endpoint."""
    with open("tests/sample.pdf", "rb") as f:
        files = {"file": ("sample.pdf", f, "application/pdf")}
        response = client.post("/api/v1/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["num_pages"] > 0
    
    # Cleanup
    doc_id = data["document_id"]
    client.delete(f"/api/v1/documents/{doc_id}")

def test_upload_invalid_file():
    """Test upload with non-PDF file."""
    files = {"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
    response = client.post("/api/v1/upload", files=files)
    
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]

def test_list_documents():
    """Test list documents endpoint."""
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total_count" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
