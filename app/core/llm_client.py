from typing import List, Dict, Optional
from openai import OpenAI
from app.config import settings
from app.utils.logger import logger

class LLMClient:
    """Client for LLM interactions - supports OpenAI."""
    
    def __init__(self, model: str = settings.llm_model):
        self.model = model
        self.provider = settings.llm_provider
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key)
            logger.info(f"Initialized OpenAI LLM with model: {model}")
        else:
            # Anthropic support (optional)
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=settings.anthropic_api_key)
                logger.info(f"Initialized Anthropic LLM with model: {model}")
            except ImportError:
                raise ImportError("Install anthropic: pip install anthropic")
    
    def generate_response(
        self,
        query: str,
        context_chunks: List[str],
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> Dict[str, any]:
        """
        Generate response using retrieved context.
        
        Args:
            query: User's question
            context_chunks: Retrieved relevant text chunks
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1, lower = more focused)
        
        Returns:
            Dict with 'response' text and metadata
        """
        # Build context from chunks
        context = "\n\n".join([
            f"[Chunk {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Create prompt
        system_prompt = """You are a helpful assistant that answers questions based on the provided context from PDF documents. 

Rules:
1. Only use information from the provided context
2. If the context doesn't contain enough information, say so
3. Cite which chunk(s) you used (e.g., "According to Chunk 2...")
4. Be concise and accurate
5. If you're unsure, acknowledge it"""

        user_prompt = f"""Context from PDF:
{context}

Question: {query}

Answer the question based on the context above. Include citations to specific chunks."""

        if self.provider == "openai":
            return self._generate_openai(system_prompt, user_prompt, max_tokens, temperature)
        else:
            return self._generate_anthropic(system_prompt, user_prompt, max_tokens, temperature)
    
    def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, any]:
        """Generate response using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise
    
    def _generate_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, any]:
        """Generate response using Anthropic (optional)."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return {
                "response": message.content[0].text,
                "model": self.model,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                    "total_tokens": message.usage.input_tokens + message.usage.output_tokens
                }
            }
        
        except Exception as e:
            logger.error(f"Anthropic generation failed: {str(e)}")
            raise
