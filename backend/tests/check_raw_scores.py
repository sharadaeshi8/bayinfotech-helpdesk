import asyncio
import sys
import os
from app.services.rag.vector_store import get_vector_store
from app.services.llm.openai_provider import OpenAIProvider

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

async def check_scores():
    print("Checking raw retrieval scores...")
    
    llm = OpenAIProvider()
    store = get_vector_store()
    
    # Test query
    query = "I can't access the lab"
    print(f"Query: {query}")
    
    embedding = await llm.get_embeddings(query)
    results = await store.search(embedding, k=3)
    
    for i, res in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Source: {res['metadata'].get('source')}")
        print(f"Raw Score (L2 Distance): {res['score']}")
        
        # Calculate current retrieval score
        retrieval_score = 1.0 / (1.0 + 0.5 * res['score'])
        print(f"Normalized Retrieval Score: {retrieval_score:.4f}")
        
        # Calculate coverage
        stop_words = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"}
        query_words = set([w for w in query.lower().split() if w not in stop_words])
        doc_words = set(res["content"].lower().split())
        intersection = query_words.intersection(doc_words)
        coverage = len(intersection) / len(query_words) if query_words else 0.0
        print(f"Coverage Score: {coverage:.4f} ({len(intersection)}/{len(query_words)} words)")

if __name__ == "__main__":
    asyncio.run(check_scores())
