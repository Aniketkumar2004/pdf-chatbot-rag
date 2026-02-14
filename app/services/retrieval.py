"""Service for retrieving relevant context and generating answers."""

from typing import Dict, List, Optional
from app.core.embeddings import EmbeddingGenerator
from app.core.vector_store import VectorStore
from app.core.llm_client import LLMClient
from app.utils.logger import logger
from app.config import settings

class RetrievalService:
    """Handles query retrieval and answer generation."""
    
    def __init__(self):
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.llm = LLMClient()
        logger.info("Initialized RetrievalService")
    
    def query(
        self,
        question: str,
        top_k: int = settings.top_k_results,
        document_id: Optional[str] = None
    ) -> Dict:
        """
        Query documents and generate answer.
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            document_id: Optional filter by document
        
        Returns:
            Dict with answer, sources, and metadata
        """
        logger.info(f"Processing query: {question[:50]}...")
        
        try:
            # Step 1: Generate query embedding
            logger.info("Generating query embedding...")
            query_embedding = self.embedder.generate_embedding(question)
            
            # Step 2: Retrieve relevant chunks
            logger.info(f"Retrieving top {top_k} chunks...")
            filter_dict = {"document_id": document_id} if document_id else None
            
            results = self.vector_store.query(
                query_embedding=query_embedding,
                n_results=top_k,
                filter_dict=filter_dict
            )
            
            if not results["documents"]:
                logger.warning("No relevant documents found")
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "document_ids": [],
                    "model_used": settings.llm_model,
                    "tokens_used": 0
                }
            
            # Step 3: Generate answer using LLM
            logger.info("Generating answer with LLM...")
            llm_response = self.llm.generate_response(
                query=question,
                context_chunks=results["documents"]
            )
            
            # Step 4: Format sources with citations
            sources = []
            document_ids = set()
            
            for i, (text, metadata, distance) in enumerate(zip(
                results["documents"],
                results["metadatas"],
                results["distances"]
            )):
                sources.append({
                    "text": text[:500] + "..." if len(text) > 500 else text,  # Truncate long chunks
                    "page_number": metadata.get("page_number", 0),
                    "chunk_index": metadata.get("chunk_index", i),
                    "relevance_score": round(distance, 3)
                })
                document_ids.add(metadata.get("document_id", "unknown"))
            
            logger.info(f"Generated answer with {len(sources)} sources")
            
            return {
                "answer": llm_response["response"],
                "sources": sources,
                "document_ids": list(document_ids),
                "model_used": llm_response["model"],
                "tokens_used": llm_response["usage"]["total_tokens"]
            }
        
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            raise
