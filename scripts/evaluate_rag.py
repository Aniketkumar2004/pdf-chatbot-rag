"""Evaluate RAG system quality."""

from app.services.ingestion import IngestionService
from app.services.retrieval import RetrievalService
from pathlib import Path
import json

def evaluate_retrieval_accuracy():
    """Test if retrieval returns relevant chunks."""
    
    # Test cases: (question, expected_keywords)
    test_cases = [
        ("What is machine learning?", ["machine learning", "artificial intelligence"]),
        ("What is RAG?", ["retrieval", "generation", "augmented"]),
    ]
    
    retrieval_service = RetrievalService()
    
    results = []
    for question, keywords in test_cases:
        result = retrieval_service.query(question, top_k=3)
        
        # Check if any keyword appears in retrieved chunks
        retrieved_text = " ".join(result["sources"][:3])
        found_keywords = [kw for kw in keywords if kw.lower() in retrieved_text.lower()]
        
        accuracy = len(found_keywords) / len(keywords)
        results.append({
            "question": question,
            "accuracy": accuracy,
            "found_keywords": found_keywords
        })
        
        print(f"Q: {question}")
        print(f"   Accuracy: {accuracy:.2%} ({len(found_keywords)}/{len(keywords)} keywords found)")
        print()
    
    avg_accuracy = sum(r["accuracy"] for r in results) / len(results)
    print(f"Average Retrieval Accuracy: {avg_accuracy:.2%}")
    
    return results

def evaluate_answer_quality():
    """Evaluate answer quality metrics."""
    
    retrieval_service = RetrievalService()
    
    test_questions = [
        "What is machine learning?",
        "Explain RAG",
        "What are the main topics in this document?"
    ]
    
    results = []
    for question in test_questions:
        result = retrieval_service.query(question)
        
        # Metrics
        answer_length = len(result["answer"].split())
        num_sources = len(result["sources"])
        has_citations = any(str(i) in result["answer"] for i in range(1, 6))
        
        results.append({
            "question": question,
            "answer_length": answer_length,
            "num_sources": num_sources,
            "has_citations": has_citations,
            "tokens_used": result.get("tokens_used", 0)
        })
        
        print(f"Q: {question}")
        print(f"   Answer length: {answer_length} words")
        print(f"   Sources used: {num_sources}")
        print(f"   Has citations: {has_citations}")
        print(f"   Tokens: {result.get('tokens_used', 0)}")
        print()
    
    return results

if __name__ == "__main__":
    print("="*60)
    print("RAG System Evaluation")
    print("="*60)
    print()
    
    print("1. Retrieval Accuracy")
    print("-" * 60)
    evaluate_retrieval_accuracy()
    
    print("\n2. Answer Quality")
    print("-" * 60)
    evaluate_answer_quality()
    
    print("\n" + "="*60)
    print("Evaluation Complete!")
    print("="*60)
