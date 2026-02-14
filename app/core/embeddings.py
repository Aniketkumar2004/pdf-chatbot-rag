from typing import List
from openai import OpenAI
from app.config import settings
from app.utils.logger import logger

class EmbeddingGenerator:
    """Generate embeddings using OpenAI API."""
    
    def __init__(self, model: str = settings.embedding_model):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model
        logger.info(f"Initialized EmbeddingGenerator with model: {model}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of text strings
            batch_size: Number of texts per API call (max 2048 for OpenAI)
        
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Generated embeddings for batch {i//batch_size + 1} ({len(batch)} texts)")
            
            except Exception as e:
                logger.error(f"Batch embedding failed at index {i}: {str(e)}")
                raise
        
        return all_embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for this model."""
        # text-embedding-3-small returns 1536 dimensions
        if "text-embedding-3-small" in self.model:
            return 1536
        elif "text-embedding-3-large" in self.model:
            return 3072
        elif "text-embedding-ada-002" in self.model:
            return 1536
        else:
            # Generate a test embedding to get dimension
            test_embedding = self.generate_embedding("test")
            return len(test_embedding)