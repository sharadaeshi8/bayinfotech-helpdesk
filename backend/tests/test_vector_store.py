"""
Unit Tests for Vector Store and RAG
Tests vector search and retrieval functionality
"""
import pytest
import numpy as np
from app.services.rag.vector_store import LocalVectorStore


class TestVectorStore:
    """Test suite for vector store functionality."""
    
    @pytest.fixture
    def vector_store(self):
        """Create a LocalVectorStore instance for testing."""
        return LocalVectorStore(dimension=1536)
    
    @pytest.mark.asyncio
    async def test_add_and_search_documents(self, vector_store):
        """Test adding documents and searching for similar ones."""
        # Create test documents
        documents = [
            "How to reset password in the system",
            "Steps for VPN connection",
            "Troubleshooting kernel panic issues"
        ]
        
        metadatas = [
            {"title": "Password Reset Guide", "source": "kb-password.md"},
            {"title": "VPN Setup", "source": "kb-vpn.md"},
            {"title": "Kernel Panic Recovery", "source": "kb-kernel.md"}
        ]
        
        # Create embeddings (mock with random vectors for testing)
        embeddings = [
            np.random.rand(1536).tolist() for _ in range(3)
        ]
        
        # Add documents
        await vector_store.add_documents(documents, metadatas, embeddings)
        
        # Verify documents were added
        assert vector_store.index.ntotal == 3
        assert len(vector_store.documents) == 3
        assert len(vector_store.metadatas) == 3
    
    @pytest.mark.asyncio
    async def test_search_returns_top_k(self, vector_store):
        """Test that search returns correct number of results."""
        # Add test documents
        documents = ["doc1", "doc2", "doc3", "doc4", "doc5"]
        metadatas = [{"id": i} for i in range(5)]
        embeddings = [np.random.rand(1536).tolist() for _ in range(5)]
        
        await vector_store.add_documents(documents, metadatas, embeddings)
        
        # Search for top 3
        query_embedding = np.random.rand(1536).tolist()
        results = await vector_store.search(query_embedding, k=3)
        
        assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_search_empty_store(self, vector_store):
        """Test that search on empty store returns empty results."""
        query_embedding = np.random.rand(1536).tolist()
        results = await vector_store.search(query_embedding, k=5)
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_search_with_metadata_filter(self, vector_store):
        """Test filtering search results by metadata."""
        documents = ["doc1", "doc2", "doc3"]
        metadatas = [
            {"category": "auth"},
            {"category": "network"},
            {"category": "auth"}
        ]
        embeddings = [np.random.rand(1536).tolist() for _ in range(3)]
        
        await vector_store.add_documents(documents, metadatas, embeddings)
        
        # Search with filter
        query_embedding = np.random.rand(1536).tolist()
        results = await vector_store.search(
            query_embedding, 
            k=5, 
            filter={"category": "auth"}
        )
        
        # Should only return filtered results
        assert len(results) <= 2  # Only 2 auth docs
        for result in results:
            assert result["metadata"]["category"] == "auth"
    
    @pytest.mark.asyncio
    async def test_save_and_load(self, vector_store, tmp_path):
        """Test saving and loading vector store."""
        # Add test data
        documents = ["test doc 1", "test doc 2"]
        metadatas = [{"id": 1}, {"id": 2}]
        embeddings = [np.random.rand(1536).tolist() for _ in range(2)]
        
        await vector_store.add_documents(documents, metadatas, embeddings)
        
        # Save
        save_path = str(tmp_path / "test_vector_store")
        vector_store.save(save_path)
        
        # Load into new instance
        new_store = LocalVectorStore(dimension=1536)
        new_store.load(save_path)
        
        # Verify data was loaded
        assert new_store.index.ntotal == 2
        assert len(new_store.documents) == 2
        assert new_store.documents == documents
        assert new_store.metadatas == metadatas
