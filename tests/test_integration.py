"""Integration tests for the complete pipeline."""

import pytest
from pathlib import Path
from app.services.ingestion import IngestionService
from app.services.retrieval import RetrievalService
import tempfile

@pytest.fixture
def ingestion_service():
    return IngestionService()

@pytest.fixture
def retrieval_service():
    return RetrievalService()

@pytest.mark.skipif(not Path("tests/sample.pdf").exists(), reason="Sample PDF not found")
def test_full_ingestion_pipeline(ingestion_service):
    """Test complete PDF ingestion pipeline."""
    result = ingestion_service.ingest_pdf(
        file_path="tests/sample.pdf",
        filename="sample.pdf"
    )
    
    assert "document_id" in result
    assert result["num_pages"] > 0
    assert result["num_chunks"] > 0
    
    # Cleanup
    ingestion_service.delete_document(result["document_id"])

@pytest.mark.skipif(True, reason="Requires API key and uploaded document")
def test_full_query_pipeline(ingestion_service, retrieval_service):
    """Test complete query pipeline."""
    # Upload document
    doc_result = ingestion_service.ingest_pdf("tests/sample.pdf", "sample.pdf")
    doc_id = doc_result["document_id"]
    
    try:
        # Query
        query_result = retrieval_service.query(
            question="What is machine learning?",
            top_k=3
        )
        
        assert "answer" in query_result
        assert len(query_result["sources"]) > 0
        assert query_result["answer"] != ""
        
    finally:
        # Cleanup
        ingestion_service.delete_document(doc_id)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
