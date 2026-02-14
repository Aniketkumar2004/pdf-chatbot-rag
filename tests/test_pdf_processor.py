import pytest
from pathlib import Path
from app.core.pdf_processor import PDFProcessor
from app.core.chunking import TextChunker
from app.core.embeddings import EmbeddingGenerator
from app.core.vector_store import VectorStore
import uuid

# You'll need a sample PDF - create one or download
SAMPLE_PDF = "tests/sample.pdf"

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

@pytest.fixture
def text_chunker():
    return TextChunker(chunk_size=500, chunk_overlap=100)

def test_pdf_extraction(pdf_processor):
    """Test PDF text extraction."""
    if not Path(SAMPLE_PDF).exists():
        pytest.skip("Sample PDF not found")
    
    result = pdf_processor.process_pdf(SAMPLE_PDF)
    
    assert "pages" in result
    assert "metadata" in result
    assert len(result["pages"]) > 0
    assert result["pages"][0]["page_number"] == 1

def test_chunking(pdf_processor, text_chunker):
    """Test text chunking."""
    if not Path(SAMPLE_PDF).exists():
        pytest.skip("Sample PDF not found")
    
    result = pdf_processor.process_pdf(SAMPLE_PDF)
    chunks = text_chunker.chunk_pages(result["pages"])
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("page_number" in chunk for chunk in chunks)

def test_embedding_generation():
    """Test embedding generation (requires API key)."""
    generator = EmbeddingGenerator()
    
    embedding = generator.generate_embedding("This is a test sentence.")
    
    assert isinstance(embedding, list)
    assert len(embedding) == 1536  # text-embedding-3-small dimension
    assert all(isinstance(x, float) for x in embedding)

def test_end_to_end_ingestion(pdf_processor, text_chunker):
    """Test complete ingestion pipeline."""
    if not Path(SAMPLE_PDF).exists():
        pytest.skip("Sample PDF not found")
    
    # Extract
    pdf_data = pdf_processor.process_pdf(SAMPLE_PDF)
    
    # Chunk
    chunks = text_chunker.chunk_pages(pdf_data["pages"])
    
    # Embed
    embedder = EmbeddingGenerator()
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.generate_embeddings_batch(texts)
    
    # Store
    vector_store = VectorStore(collection_name="test_collection")
    doc_id = str(uuid.uuid4())
    
    vector_store.add_documents(
        chunks=chunks,
        embeddings=embeddings,
        document_id=doc_id,
        metadata=pdf_data["metadata"]
    )
    
    # Verify
    count = vector_store.get_document_count()
    assert count >= len(chunks)
    
    # Cleanup
    vector_store.delete_document(doc_id)