from typing import List, Dict

# Updated import - try new location first, fallback to old
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Fallback to old import for older langchain versions
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings
from app.utils.logger import logger

class TextChunker:
    """Split text into chunks with overlap for RAG."""
    
    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # RecursiveCharacterTextSplitter tries to split on paragraphs, then sentences
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_pages(self, pages: List[Dict]) -> List[Dict]:
        """
        Chunk text from pages with metadata.
        
        Args:
            pages: List of dicts with 'page_number' and 'text'
        
        Returns:
            List of chunk dicts with text, page_number, chunk_index
        """
        all_chunks = []
        global_chunk_index = 0
        
        for page_data in pages:
            page_num = page_data["page_number"]
            page_text = page_data["text"]
            
            # Split this page's text
            text_chunks = self.splitter.split_text(page_text)
            
            # Add metadata to each chunk
            for local_idx, chunk_text in enumerate(text_chunks):
                all_chunks.append({
                    "text": chunk_text,
                    "page_number": page_num,
                    "chunk_index": global_chunk_index,
                    "local_chunk_index": local_idx,  # Chunk index within this page
                    "chunk_length": len(chunk_text)
                })
                global_chunk_index += 1
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(pages)} pages")
        return all_chunks
    
    def chunk_document(self, full_text: str, doc_id: str = None) -> List[Dict]:
        """
        Chunk entire document text (when page numbers aren't available).
        
        Args:
            full_text: Complete document text
            doc_id: Optional document identifier
        
        Returns:
            List of chunk dicts
        """
        chunks = self.splitter.split_text(full_text)
        
        return [
            {
                "text": chunk,
                "chunk_index": idx,
                "chunk_length": len(chunk),
                "doc_id": doc_id
            }
            for idx, chunk in enumerate(chunks)
        ]
