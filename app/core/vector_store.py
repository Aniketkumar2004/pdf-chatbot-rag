"""Simple in-memory vector store using basic Python data structures."""

from typing import List, Dict, Optional
import numpy as np
from app.config import settings
from app.utils.logger import logger

class VectorStore:
    """Simple in-memory vector store - no persistence issues."""
    
    def __init__(self, collection_name: str = settings.collection_name, persist_dir: str = None):
        """Initialize in-memory storage."""
        self.collection_name = collection_name
        self.documents = []  # List of document texts
        self.embeddings = []  # List of embedding vectors
        self.metadatas = []  # List of metadata dicts
        self.ids = []  # List of IDs
        logger.info(f"Initialized simple in-memory VectorStore")
    
    def add_documents(
        self,
        chunks: List[Dict],
        embeddings: List[List[float]],
        document_id: str,
        metadata: Dict = None
    ):
        """Add documents to the store."""
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings")
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{document_id}_chunk_{chunk['chunk_index']}"
            
            # Store data
            self.ids.append(chunk_id)
            self.documents.append(chunk["text"])
            self.embeddings.append(embedding)
            
            # Store metadata
            chunk_meta = {
                "document_id": document_id,
                "page_number": chunk.get("page_number", 0),
                "chunk_index": chunk["chunk_index"],
                "chunk_length": chunk["chunk_length"]
            }
            if metadata:
                chunk_meta.update({
                    "filename": metadata.get("filename", ""),
                    "num_pages": metadata.get("num_pages", 0)
                })
            self.metadatas.append(chunk_meta)
        
        logger.info(f"Added {len(chunks)} chunks for document {document_id}")
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = settings.top_k_results,
        filter_dict: Optional[Dict] = None
    ) -> Dict:
        """Query for similar documents using cosine similarity."""
        if not self.embeddings:
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}
        
        # Calculate cosine similarities
        query_array = np.array(query_embedding)
        similarities = []
        
        for i, emb in enumerate(self.embeddings):
            # Apply filter if provided
            if filter_dict:
                match = all(
                    self.metadatas[i].get(k) == v 
                    for k, v in filter_dict.items()
                )
                if not match:
                    continue
            
            # Cosine similarity
            emb_array = np.array(emb)
            similarity = np.dot(query_array, emb_array) / (
                np.linalg.norm(query_array) * np.linalg.norm(emb_array)
            )
            # Convert to distance (lower is better)
            distance = 1 - similarity
            similarities.append((i, distance))
        
        # Sort by distance (ascending)
        similarities.sort(key=lambda x: x[1])
        
        # Get top N results
        top_results = similarities[:n_results]
        
        return {
            "ids": [self.ids[i] for i, _ in top_results],
            "documents": [self.documents[i] for i, _ in top_results],
            "metadatas": [self.metadatas[i] for i, _ in top_results],
            "distances": [dist for _, dist in top_results]
        }
    
    def delete_document(self, document_id: str):
        """Delete all chunks for a document."""
        indices_to_remove = [
            i for i, meta in enumerate(self.metadatas)
            if meta.get("document_id") == document_id
        ]
        
        # Remove in reverse order to avoid index shifting
        for i in sorted(indices_to_remove, reverse=True):
            del self.ids[i]
            del self.documents[i]
            del self.embeddings[i]
            del self.metadatas[i]
        
        logger.info(f"Deleted {len(indices_to_remove)} chunks for document {document_id}")
    
    def get_document_count(self) -> int:
        """Get total number of chunks."""
        return len(self.documents)
    
    def list_documents(self) -> List[str]:
        """List all unique document IDs."""
        doc_ids = set(meta.get("document_id", "") for meta in self.metadatas)
        return list(doc_ids)
