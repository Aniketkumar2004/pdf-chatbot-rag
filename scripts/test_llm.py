from app.core.llm_client import LLMClient

# Initialize client
llm = LLMClient()

# Test generation
context_chunks = [
    "Machine learning is a subset of artificial intelligence.",
    "RAG stands for Retrieval-Augmented Generation."
]

response = llm.generate_response(
    query="What is RAG?",
    context_chunks=context_chunks
)

print("\n=== LLM Response ===")
print(response["response"])
print(f"\nModel: {response['model']}")
print(f"Tokens used: {response['usage']['total_tokens']}")
