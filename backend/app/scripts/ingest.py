import asyncio
import os
import glob
from typing import List, Dict, Any
from app.services.llm.openai_provider import OpenAIProvider
from app.services.rag.vector_store import get_vector_store, LocalVectorStore
from app.core.config import settings

def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Simple frontmatter parser."""
    if not content.startswith("---"):
        return {}, content
    
    try:
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content
        
        yaml_content = parts[1]
        body = parts[2].strip()
        
        metadata = {}
        for line in yaml_content.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                # Basic cleanup
                if value.startswith("[") and value.endswith("]"):
                    # List parsing
                    value = [v.strip().strip("'").strip('"') for v in value[1:-1].split(",")]
                metadata[key] = value
                
        return metadata, body
    except Exception as e:
        print(f"Error parsing frontmatter: {e}")
        return {}, content

async def ingest_kb_docs(kb_dir: str):
    print(f"Ingesting KB documents from {kb_dir}...")
    
    # Initialize database if using PostgreSQL
    if settings.VECTOR_STORE_TYPE == "postgres":
        print("Initializing PostgreSQL database...")
        from app.core.database import init_db
        await init_db()
        print("Database initialized.")
    
    files = glob.glob(os.path.join(kb_dir, "*.md"))
    if not files:
        print("No Markdown files found.")
        return

    # Initialize LLM
    if not settings.OPENAI_API_KEY:
        print("No OPENAI_API_KEY found. Using MockLLMProvider.")
        from app.services.llm.mock_provider import MockLLMProvider
        llm = MockLLMProvider()
    else:
        llm = OpenAIProvider()
    
    vector_store = get_vector_store()
    
    all_chunks = []
    all_metadatas = []
    all_embeddings = []
    
    for file_path in files:
        print(f"Processing {os.path.basename(file_path)}...")
        with open(file_path, "r") as f:
            content = f.read()
            
        metadata, body = parse_frontmatter(content)
        
        # Add source filename to metadata
        metadata["source"] = os.path.basename(file_path)
        
        # Chunking (Simple chunking)
        chunk_size = 1000 # Larger chunks for KB articles to keep context
        overlap = 100
        
        start = 0
        while start < len(body):
            end = start + chunk_size
            chunk = body[start:end]
            
            # Create a rich context string for the chunk
            # This helps the LLM understand what this chunk is about even if it's in the middle
            rich_chunk = f"Document: {metadata.get('title', 'Unknown')}\nCategory: {metadata.get('category', 'General')}\nContent:\n{chunk}"
            
            all_chunks.append(rich_chunk)
            all_metadatas.append(metadata)
            start += (chunk_size - overlap)

    print(f"Created {len(all_chunks)} chunks from {len(files)} files.")
    
    # Generate embeddings in batches
    batch_size = 10
    for i in range(0, len(all_chunks), batch_size):
        batch_chunks = all_chunks[i:i+batch_size]
        print(f"Embedding batch {i//batch_size + 1}...")
        
        for chunk in batch_chunks:
            emb = await llm.get_embeddings(chunk)
            all_embeddings.append(emb)
            
    # Store in vector store
    await vector_store.add_documents(all_chunks, all_metadatas, all_embeddings)
    
    # Save to disk (only for local vector store)
    if settings.VECTOR_STORE_TYPE == "local":
        vector_store.save("vector_store_data")
        print("Ingestion complete and saved to disk.")
    else:
        print("Ingestion complete and saved to PostgreSQL.")


if __name__ == "__main__":
    kb_directory = "data/kb"
    # Adjust path if running from root
    if not os.path.exists(kb_directory):
        kb_directory = "app/data/kb" # Try alternative
        
    # Absolute fallback
    if not os.path.exists(kb_directory):
        kb_directory = "/home/dev/Desktop/assesment/bayinfotech-helpdesk/backend/data/kb"

    if os.path.exists(kb_directory):
        asyncio.run(ingest_kb_docs(kb_directory))
    else:
        print(f"KB Directory not found: {kb_directory}")
