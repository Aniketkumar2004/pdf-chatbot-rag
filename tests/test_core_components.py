"""Unit tests for core components."""

import pytest
from app.core.pdf_processor import PDFProcessor
from app.core.chunking import TextChunker
from app.core.embeddings import EmbeddingGenerator
from app.core.vector_store import VectorStore
from pathlib import Path

# PDF Processor Tests
def test_pdf_processor_initialization():
    """Test PDF processor can be initialized."""
    processor = PDFProcessor()
    assert processor is not None
    assert "pypdf" in processor.supported_methods

def test_clean_text():
    """Test text cleaning functionality."""
    processor = PDFProcessor()
    dirty_text = "Hello\x00World\ufffdTest"
    clean = processor.clean_text(dirty_text)
    assert "\x00" not in clean
    assert "\ufffd" not in clean

# Chunking Tests
def test_text_chunker_initialization():
    """Test chunker initialization with custom settings."""
    chunker = TextChunker(chunk_size=500, chunk_overlap=100)
    assert chunker.chunk_size == 500
    assert chunker.chunk_overlap == 100

def test_chunking_preserves_page_numbers():
    """Test that page numbers are preserved in chunks."""
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    pages = [
        {"page_number": 1, "text": "This is page one. " * 10},
        {"page_number": 2, "text": "This is page two. " * 10}
    ]
    chunks = chunker.chunk_pages(pages)
    
    assert len(chunks) > 0
    assert all("page_number" in chunk for chunk in chunks)
    assert chunks[0]["page_number"] == 1

# Embedding Tests
@pytest.mark.skipif(True, reason="Requires API key")
def test_embedding_generation():
    """Test embedding generation."""
    generator = EmbeddingGenerator()
    embedding = generator.generate_embedding("test text")
    
    assert isinstance(embedding, list)
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)

# Vector Store Tests
def test_vector_store_initialization():
    """Test vector store initialization."""
    store = VectorStore(collection_name="test_collection")
    assert store is not None
    assert store.get_document_count() == 0

def test_vector_store_add_and_query():
    """Test adding documents and querying."""
    store = VectorStore(collection_name="test_collection_2")
    
    # Add test document
    chunks = [{
        "text": "Machine learning is a subset of AI",
        "page_number": 1,
        "chunk_index": 0,
        "chunk_length": 38
    }]
    embeddings = [[0.1] * 1536]
    
    store.add_documents(chunks, embeddings, "test-doc", {"filename": "test.pdf"})
    
    # Verify count
    assert store.get_document_count() == 1
    
    # Query
    results = store.query([0.1] * 1536, n_results=1)
    assert len(results["documents"]) == 1
    assert "Machine learning" in results["documents"][0]

def test_vector_store_delete():
    """Test document deletion."""
    store = VectorStore(collection_name="test_collection_3")
    
    # Add document
    chunks = [{
        "text": "Test text",
        "page_number": 1,
        "chunk_index": 0,
        "chunk_length": 9
    }]
    store.add_documents(chunks, [[0.1] * 1536], "delete-test", {})
    
    # Verify added
    assert store.get_document_count() == 1
    
    # Delete
    store.delete_document("delete-test")
    
    # Verify deleted
    assert store.get_document_count() == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
