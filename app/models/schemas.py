"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Models

class QueryRequest(BaseModel):
    """Request model for querying documents."""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    document_id: Optional[str] = Field(None, description="Filter by specific document ID")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of chunks to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is machine learning?",
                "document_id": None,
                "top_k": 5
            }
        }

class DeleteDocumentRequest(BaseModel):
    """Request model for deleting a document."""
    document_id: str = Field(..., description="Document ID to delete")

# Response Models

class SourceChunk(BaseModel):
    """Model for a source chunk with citation info."""
    text: str
    page_number: int
    chunk_index: int
    relevance_score: float = Field(..., description="Similarity score (lower is better)")

class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceChunk] = Field(..., description="Source chunks with citations")
    document_ids: List[str] = Field(..., description="Documents used in answer")
    model_used: str = Field(..., description="LLM model used")
    tokens_used: Optional[int] = Field(None, description="Total tokens consumed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Machine learning is a subset of AI that enables systems to learn from data.",
                "sources": [
                    {
                        "text": "Machine learning is...",
                        "page_number": 1,
                        "chunk_index": 0,
                        "relevance_score": 0.15
                    }
                ],
                "document_ids": ["doc-123"],
                "model_used": "gpt-3.5-turbo",
                "tokens_used": 450
            }
        }

class UploadResponse(BaseModel):
    """Response model for upload endpoint."""
    document_id: str
    filename: str
    num_pages: int
    num_chunks: int
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc-abc-123",
                "filename": "research_paper.pdf",
                "num_pages": 15,
                "num_chunks": 42,
                "message": "Document uploaded and processed successfully"
            }
        }

class DocumentInfo(BaseModel):
    """Model for document metadata."""
    document_id: str
    filename: str
    num_pages: int
    num_chunks: int
    upload_timestamp: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None

class ListDocumentsResponse(BaseModel):
    """Response model for listing documents."""
    documents: List[DocumentInfo]
    total_count: int

class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    document_id: str
    message: str
    success: bool

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    vector_store_count: int
    version: str = "1.0.0"
