"""FastAPI routes for the PDF chatbot."""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
import shutil
from pathlib import Path
from datetime import datetime
import tempfile

from app.models.schemas import (
    QueryRequest, QueryResponse, UploadResponse,
    DeleteDocumentRequest, DeleteResponse,
    ListDocumentsResponse, DocumentInfo, HealthResponse
)
from app.services.ingestion import IngestionService
from app.services.retrieval import RetrievalService
from app.config import settings
from app.utils.logger import logger

# Initialize router
router = APIRouter()

# Initialize services (these will be reused across requests)
ingestion_service = IngestionService()
retrieval_service = RetrievalService()

# Health Check
@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check if the service is running and healthy."""
    try:
        chunk_count = ingestion_service.get_document_count()
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            vector_store_count=chunk_count
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

# Upload PDF
@router.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF document.
    
    - **file**: PDF file to upload (max 10MB by default)
    
    Returns document_id and processing stats.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Create a temporary file to save the upload
    temp_file = None
    try:
        # Create temp file with .pdf extension
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Read file content in binary mode
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        logger.info(f"Saved uploaded file to temp: {temp_path}")
        
        # Validate file size
        file_size = Path(temp_path).stat().st_size
        max_size = settings.max_file_size_mb * 1024 * 1024
        
        if file_size > max_size:
            Path(temp_path).unlink()  # Delete temp file
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        # Process the PDF
        result = ingestion_service.ingest_pdf(
            file_path=temp_path,
            filename=file.filename
        )
        
        # Clean up temp file
        Path(temp_path).unlink()
        
        return UploadResponse(
            document_id=result["document_id"],
            filename=result["filename"],
            num_pages=result["num_pages"],
            num_chunks=result["num_chunks"],
            message="Document uploaded and processed successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        
        # Clean up temp file on error
        if temp_file and Path(temp_file.name).exists():
            Path(temp_file.name).unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )

# Query Documents
@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_documents(request: QueryRequest):
    """
    Ask a question and get an answer based on uploaded documents.
    
    - **question**: Your question (1-1000 characters)
    - **document_id**: Optional - filter by specific document
    - **top_k**: Number of relevant chunks to retrieve (1-20)
    
    Returns answer with citations and source chunks.
    """
    try:
        result = retrieval_service.query(
            question=request.question,
            top_k=request.top_k or settings.top_k_results,
            document_id=request.document_id
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        logger.error(f"Query failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )

# List Documents
@router.get("/documents", response_model=ListDocumentsResponse, tags=["Documents"])
async def list_documents():
    """
    List all uploaded documents.
    
    Returns list of document IDs and metadata.
    """
    try:
        doc_ids = ingestion_service.list_documents()
        
        # For now, return basic info
        documents = [
            DocumentInfo(
                document_id=doc_id,
                filename="unknown",
                num_pages=0,
                num_chunks=0
            )
            for doc_id in doc_ids
        ]
        
        return ListDocumentsResponse(
            documents=documents,
            total_count=len(documents)
        )
    
    except Exception as e:
        logger.error(f"List documents failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )

# Delete Document
@router.delete("/documents/{document_id}", response_model=DeleteResponse, tags=["Documents"])
async def delete_document(document_id: str):
    """
    Delete a document from the system.
    
    - **document_id**: ID of document to delete
    
    Removes all chunks and embeddings for this document.
    """
    try:
        success = ingestion_service.delete_document(document_id)
        
        if success:
            return DeleteResponse(
                document_id=document_id,
                message=f"Document {document_id} deleted successfully",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )

# Get Document Info
@router.get("/documents/{document_id}", response_model=DocumentInfo, tags=["Documents"])
async def get_document_info(document_id: str):
    """
    Get detailed information about a specific document.
    
    - **document_id**: ID of the document
    """
    return DocumentInfo(
        document_id=document_id,
        filename="Document details not implemented",
        num_pages=0,
        num_chunks=0
    )
