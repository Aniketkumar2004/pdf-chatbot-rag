"""Service for ingesting PDFs into the system."""

import uuid
from pathlib import Path
from typing import Dict
from app.core.pdf_processor import PDFProcessor
from app.core.chunking import TextChunker
from app.core.embeddings import EmbeddingGenerator
from app.core.vector_store import VectorStore
from app.utils.logger import logger
from app.config import settings

class IngestionService:
    """Handles PDF upload and processing pipeline."""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.chunker = TextChunker()
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()
        logger.info("Initialized IngestionService")
    
    def ingest_pdf(self, file_path: str, filename: str) -> Dict:
        """
        Complete ingestion pipeline for a PDF.
        
        Args:
            file_path: Path to uploaded PDF file
            filename: Original filename
        
        Returns:
            Dict with document_id, num_pages, num_chunks
        """
        logger.info(f"Starting ingestion for: {filename}")
        
        # Generate unique document ID
        document_id = f"doc-{uuid.uuid4().hex[:12]}"
        
        try:
            # Step 1: Extract text from PDF
            logger.info(f"[{document_id}] Extracting text from PDF...")
            pdf_data = self.pdf_processor.process_pdf(file_path)
            num_pages = pdf_data["metadata"]["num_pages"]
            logger.info(f"[{document_id}] Extracted {num_pages} pages")
            
            # Step 2: Chunk the text
            logger.info(f"[{document_id}] Chunking text...")
            chunks = self.chunker.chunk_pages(pdf_data["pages"])
            num_chunks = len(chunks)
            logger.info(f"[{document_id}] Created {num_chunks} chunks")
            
            # Step 3: Generate embeddings
            logger.info(f"[{document_id}] Generating embeddings...")
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedder.generate_embeddings_batch(texts)
            logger.info(f"[{document_id}] Generated {len(embeddings)} embeddings")
            
            # Step 4: Store in vector database
            logger.info(f"[{document_id}] Storing in vector database...")
            metadata = {
                "filename": filename,
                "title": pdf_data["metadata"].get("title", "Unknown"),
                "author": pdf_data["metadata"].get("author", "Unknown"),
                "num_pages": num_pages
            }
            
            self.vector_store.add_documents(
                chunks=chunks,
                embeddings=embeddings,
                document_id=document_id,
                metadata=metadata
            )
            
            logger.info(f"[{document_id}] Ingestion complete!")
            
            return {
                "document_id": document_id,
                "filename": filename,
                "num_pages": num_pages,
                "num_chunks": num_chunks,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"[{document_id}] Ingestion failed: {str(e)}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document from vector store."""
        try:
            self.vector_store.delete_document(document_id)
            logger.info(f"Deleted document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {document_id}: {str(e)}")
            return False
    
    def list_documents(self) -> list:
        """List all documents in the system."""
        try:
            doc_ids = self.vector_store.list_documents()
            logger.info(f"Found {len(doc_ids)} documents")
            return doc_ids
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            return []
    
    def get_document_count(self) -> int:
        """Get total chunk count."""
        return self.vector_store.get_document_count()
