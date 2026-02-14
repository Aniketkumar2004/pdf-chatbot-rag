from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal, Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    
    # Environment
    environment: Literal["development", "production"] = Field(default="development")
    log_level: str = Field(default="INFO")
    
    # File Upload
    max_file_size_mb: int = Field(default=10)
    allowed_extensions: str = Field(default="pdf")
    upload_dir: str = Field(default="./data/uploads")
    
    # Vector Store
    chroma_persist_dir: str = Field(default="./data/chroma_db")
    collection_name: str = Field(default="pdf_documents")
    
    # Chunking
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    
    # Retrieval
    top_k_results: int = Field(default=5)
    similarity_threshold: float = Field(default=0.7)
    
    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # Model names
    embedding_model: str = Field(default="text-embedding-3-small")
    llm_model: str = Field(default="gpt-3.5-turbo")
    
    # LLM Provider: "openai" or "anthropic"
    llm_provider: Literal["openai", "anthropic"] = Field(default="openai")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def validate_api_keys(self):
        """Ensure required API keys are present based on provider."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic LLM")

# Global settings instance
settings = Settings()

# Validate on import
settings.validate_api_keys()

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.chroma_persist_dir, exist_ok=True)
