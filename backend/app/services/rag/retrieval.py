from typing import List, Dict, Any
from app.services.llm.base import LLMProvider
from app.services.rag.vector_store import VectorStore
from app.core.logging import get_logger

logger = get_logger(__name__)

class RAGService:
    def __init__(self, llm_provider: LLMProvider, vector_store: VectorStore):
        self.llm = llm_provider
        self.vector_store = vector_store

    async def retrieve_context(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # 1. Generate embedding for the query
        query_embedding = await self.llm.get_embeddings(query)
        
        # 2. Search vector store
        results = await self.vector_store.search(query_embedding, k=k)
        
        # 3. Deduplicate results based on source filename
        unique_results = []
        seen_sources = set()
        
        for res in results:
            source = res["metadata"].get("source")
            if source and source not in seen_sources:
                seen_sources.add(source)
                unique_results.append(res)
            elif not source:
                # If no source metadata, keep it (unlikely with current ingest)
                unique_results.append(res)
                
        return unique_results

    async def generate_response(self, query: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        # 1. Retrieve context
        retrieved_docs = await self.retrieve_context(query)
        
        # 2. Format context
        context_str = "\n\n".join([
            f"[{doc['metadata'].get('id', 'Unknown')} v{doc['metadata'].get('version', '1.0')}, Category: {doc['metadata'].get('category', 'General')}, Last Updated: {doc['metadata'].get('last_updated', 'Unknown')}]\nContent: {doc['content']}\n---" 
            for doc in retrieved_docs
        ])
        
        # 3. Generate answer
        answer = await self.llm.generate_answer(query, context_str, history)
        
        # 4. Calculate component scores for the top result (if any)
        components = {
            "retrieval_score": 0.0,
            "coverage_score": 0.0,
            "recency_score": 0.0
        }
        
        if retrieved_docs:
            top_doc = retrieved_docs[0]
            
            # A. Retrieval Score (Normalized L2 distance)
            # Assuming L2 distance where 0 is perfect match. 
            # We want 0->1, large->0. 
            # Heuristic: 1 / (1 + 0.3 * distance) to be even less punitive for high-dim vectors
            raw_score = top_doc.get("score", 1.0)
            components["retrieval_score"] = 1.0 / (1.0 + 0.3 * raw_score)
            
            # B. Coverage Score (Keyword overlap)
            # Check if query words (minus stop words) appear in the document content
            stop_words = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"}
            
            query_words = [w for w in query.lower().split() if w not in stop_words]
            doc_content = top_doc["content"].lower()
            
            if query_words:
                # Count how many query words appear as substrings in the doc
                matches = sum(1 for w in query_words if w in doc_content)
                components["coverage_score"] = matches / len(query_words)
            else:
                components["coverage_score"] = 0.0
            
            # C. Recency Score (Decay based on last_updated)
            import datetime
            last_updated_str = top_doc["metadata"].get("last_updated")
            if last_updated_str:
                try:
                    last_updated = datetime.datetime.strptime(last_updated_str, "%Y-%m-%d")
                    now = datetime.datetime.now()
                    days_diff = (now - last_updated).days
                    # Decay: 1.0 at 0 days, 0.5 at 365 days
                    # Formula: 1 / (1 + days/365)
                    components["recency_score"] = 1.0 / (1.0 + max(0, days_diff)/365.0)
                except ValueError:
                    components["recency_score"] = 0.5 # Default if format error
            else:
                components["recency_score"] = 0.5 # Default if missing
        
        return {
            "answer": answer,
            "sources": retrieved_docs,
            "components": components
        }
