from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import faiss
import numpy as np
import pickle
import os
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class VectorStore(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add documents and their embeddings to the store."""
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    def save(self, path: str):
        """Save the vector store to disk."""
        pass
    
    @abstractmethod
    def load(self, path: str):
        """Load the vector store from disk."""
        pass

class LocalVectorStore(VectorStore):
    def __init__(self, dimension: int = 1536): # Default for text-embedding-3-small
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.metadatas = []
        
    async def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        if not documents:
            return
            
        vectors = np.array(embeddings).astype('float32')
        self.index.add(vectors)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)

    async def search(self, query_embedding: List[float], k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []
            
        vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.documents):
                # Basic filtering (exact match on metadata fields)
                if filter:
                    match = True
                    for key, value in filter.items():
                        if self.metadatas[idx].get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                        
                results.append({
                    "content": self.documents[idx],
                    "metadata": self.metadatas[idx],
                    "score": float(distances[0][i])
                })
        
        return results

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "data.pkl"), "wb") as f:
            pickle.dump({"documents": self.documents, "metadatas": self.metadatas}, f)

    def load(self, path: str):
        if not os.path.exists(os.path.join(path, "index.faiss")):
            return
            
        self.index = faiss.read_index(os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "data.pkl"), "rb") as f:
            data = pickle.load(f)
            self.documents = data["documents"]
            self.metadatas = data["metadatas"]

class PgVectorStore(VectorStore):
    """PostgreSQL vector store using pgvector extension."""
    
    def __init__(self):
        from app.core.database import AsyncSessionLocal
        self.session_factory = AsyncSessionLocal
        
    async def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        from app.models.models import Document
        from sqlalchemy import delete
        
        if not documents:
            return
        
        async with self.session_factory() as session:
            try:
                # Clear existing documents (for re-ingestion)
                await session.execute(delete(Document))
                
                # Add new documents
                for doc, metadata, embedding in zip(documents, metadatas, embeddings):
                    db_doc = Document(
                        content=doc,
                        embedding=embedding,
                        doc_metadata=metadata
                    )
                    session.add(db_doc)
                
                await session.commit()
                logger.info(f"Added {len(documents)} documents to PostgreSQL vector store")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error adding documents to vector store: {e}")
                raise

    async def search(self, query_embedding: List[float], k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        from app.models.models import Document
        from sqlalchemy import select, func
        
        async with self.session_factory() as session:
            try:
                # Build query with cosine distance
                query = select(
                    Document.content,
                    Document.doc_metadata,
                    Document.embedding.cosine_distance(query_embedding).label("distance")
                ).order_by("distance").limit(k)
                
                # Apply metadata filters if provided
                if filter:
                    for key, value in filter.items():
                        query = query.where(Document.doc_metadata[key].astext == str(value))
                
                result = await session.execute(query)
                rows = result.all()
                
                # Format results
                results = []
                for row in rows:
                    results.append({
                        "content": row.content,
                        "metadata": row.doc_metadata,  # Return as 'metadata' key for compatibility
                        "score": float(row.distance)  # Cosine distance (0 = identical, 2 = opposite)
                    })
                
                return results
                
            except Exception as e:
                logger.error(f"Error searching vector store: {e}")
                return []

    def save(self, path: str):
        """Not needed for PostgreSQL - data is persisted in database."""
        pass

    def load(self, path: str):
        """Not needed for PostgreSQL - data is loaded from database."""
        pass

# Factory to get the configured vector store
def get_vector_store() -> VectorStore:
    if settings.VECTOR_STORE_TYPE == "postgres":
        if not hasattr(get_vector_store, "_pg_instance"):
            get_vector_store._pg_instance = PgVectorStore()
        return get_vector_store._pg_instance
    elif settings.VECTOR_STORE_TYPE == "local":
        # Singleton-ish for local store in memory (for now)
        if not hasattr(get_vector_store, "_instance"):
            store = LocalVectorStore()
            # Try to load if exists
            store.load("vector_store_data")
            get_vector_store._instance = store
        return get_vector_store._instance
    else:
        raise NotImplementedError(f"Vector store type {settings.VECTOR_STORE_TYPE} not implemented")
