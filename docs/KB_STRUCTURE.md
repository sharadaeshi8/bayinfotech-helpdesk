# Knowledge Base Structure Documentation

## Overview

The Knowledge Base (KB) is the foundation of the AI Help Desk's Retrieval Augmented Generation (RAG) system. It contains **34 synthetic documents** covering authentication, lab operations, troubleshooting, and support policies.

---

## KB Storage

### File Location

**Path:** `backend/data/kb/`

**Format:** Markdown (.md files)

**Total Documents:** 34

### Document Categories

```
backend/data/kb/
├── Platform & Authentication (7 docs)
│   ├── 00-platform-overview.md
│   ├── 01-access-and-authentication-v2.1.md
│   ├── 02-authentication-policy-2023.md
│   ├── 03-authentication-policy-2024.md
│   ├── kb-password-reset.md
│   ├── kb-mfa-reset.md
│   └── kb-auth-loop.md
│
├── Lab Operations (8 docs)
│   ├── 04-virtual-lab-operations-and-recovery.md
│   ├── kb-lab-setup-guide.md
│   ├── kb-environment-reset.md
│   ├── kb-wrong-environment.md
│   ├── kb-session-timeout.md
│   ├── kb-toolset-mismatch.md
│   ├── kb-vm-crash-recovery.md
│   └── kb-access-training-materials.md
│
├── Infrastructure & Network (7 docs)
│   ├── 05-environment-mapping-and-routing.md
│   ├── 06-container-runtime-troubleshooting.md
│   ├── 07-dns-and-network-troubleshooting.md
│   ├── kb-container-init-failure.md
│   ├── kb-dns-resolution.md
│   ├── kb-network-connectivity.md
│   └── kb-time-drift-auth.md
│
├── Security & Monitoring (5 docs)
│   ├── 08-logging-monitoring-and-security-controls.md
│   ├── kb-logging-configuration.md
│   ├── kb-system-monitoring.md
│   ├── kb-kernel-panic.md
│   └── kb-data-recovery.md
│
└── Policies & Support (7 docs)
    ├── 09-tiering-escalation-and-sla-policy.md
    ├── 10-known-error-catalog.md
    ├── kb-escalation-policy.md
    ├── kb-permissions-roles.md
    ├── kb-performance-issues.md
    ├── kb-hosts-file-policy.md
    └── kb-conflicting-kb-docs.md
```

---

## Document Structure

### Example Document Format

**File:** `kb-password-reset.md`

```markdown
# Password Reset Guide

## Overview
This guide covers password reset procedures for all PCTE users.

## Prerequisites
- Access to registered email address
- Valid user account

## Procedure

### Step 1: Navigate to Login Page
Go to https://pcte.example.com/login

### Step 2: Click "Forgot Password"
Located below the password field

### Step 3: Enter Email
Provide your registered email address

### Step 4: Check Email
Reset link expires in 15 minutes

### Step 5: Set New Password
Password requirements:
- Minimum 12 characters
- At least one uppercase letter
- At least one number
- At least one special character

## Troubleshooting

### Email Not Received
- Check spam folder
- Verify email address spelling
- Wait 5 minutes before requesting new link

### Link Expired
Request new reset link

## Related Resources
- [MFA Reset Guide](kb-mfa-reset.md)
- [Account Lockout Policy](02-authentication-policy-2024.md)
```

### Metadata in Documents

Documents contain implicit metadata:
- **Title:** First H1 heading
- **Category:** Inferred from filename/content
- **Sections:** H2/H3 headings
- **Related Docs:** Links to other KB articles

---

## KB Ingestion Process

### Ingestion Script

**Location:** `backend/app/scripts/ingest.py`

**Purpose:** Process KB documents and create vector embeddings

### Ingestion Flow

```
1. Read Markdown Files
   ↓
2. Parse Document
   ├→ Extract title (first H1)
   ├→ Extract content (full text)
   └→ Generate metadata
   ↓
3. Chunk Document
   ├→ Split by sections (H2/H3)
   ├→ Max chunk size: ~500 tokens
   └→ Overlap: 50 tokens
   ↓
4. Generate Embeddings
   ├→ OpenAI text-embedding-3-small
   ├→ Dimension: 1536
   └→ Rate limiting: 3000 RPM
   ↓
5. Store in PostgreSQL
   ├→ documents table
   ├→ Text + embedding + metadata
   └→ Create vector index (cosine similarity)
```

### Running Ingestion

```bash
# Method 1: Direct script
cd backend
python -m app.scripts.ingest

# Method 2: Docker container
docker-compose exec backend python -m app.scripts.ingest

# Method 3: With environment
source venv/bin/activate
export OPENAI_API_KEY="..."
export DATABASE_URL_OVERRIDE="postgresql://..."
python -m app.scripts.ingest
```

### Ingestion Script Code Structure

**Key Functions:**

```python
async def ingest_knowledge_base():
    """Main ingestion function"""
    # 1. Initialize database
    await init_db()
    
    # 2. Initialize services
    llm = OpenAIProvider()
    vector_store = PgVectorStore()
    
    # 3. Read KB files
    kb_files = glob("data/kb/*.md")
    
    # 4. Process each file
    for file in kb_files:
        text = read_file(file)
        chunks = chunk_document(text)
        
        # 5. Generate embeddings
        embeddings = await llm.get_embeddings(chunks)
        
        # 6. Store in vector DB
        await vector_store.add_documents(
            texts=chunks,
            embeddings=embeddings,
            metadata={"title": ..., "source": file}
        )
```

---

## Vector Indexing

### Database Schema

**Table:** `documents`

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    doc_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector similarity index
CREATE INDEX documents_embedding_idx 
ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Column Descriptions:**
- `id` - Unique document chunk identifier
- `text` - Actual text content (RAW, not preprocessed)
- `embedding` - 1536-dimensional vector (OpenAI embedding)
- `doc_metadata` - JSON containing `{title, source, category, section}`
- `created_at` - Timestamp for tracking

### Vector Index Types

**Current:** IVFFlat (Inverted File Flat)
- Fast approximate search
- Good for 10K-1M vectors
- `lists=100` (cluster count)

**Alternative:** HNSW (Hierarchical Navigable Small World)
- Better recall
- Slower index build
- Ideal for production scale

### Similarity Metrics

**Cosine Similarity** (default):
```sql
SELECT * FROM documents
ORDER BY embedding <=> query_embedding
LIMIT 3;
```

**Operators:**
- `<=>` - Cosine distance
- `<#>` - Negative inner product
- `<->` - Euclidean distance

---

## RAG Retrieval Process

### Query-Time Flow

```
1. User Question
   ↓
2. Generate Query Embedding
   ├→ Same model as indexing (text-embedding-3-small)
   └→ 1536 dimensions
   ↓
3. Vector Search
   ├→ SELECT * FROM documents
   │  ORDER BY embedding <=> query_embedding
   │  LIMIT 3
   └→ Returns: [chunk1, chunk2, chunk3]
   ↓
4. Retrieve Metadata
   ├→ Document titles
   ├→ Source files
   └→ Categories
   ↓
5. Format Context
   └→ "Document: [title]\n[chunk text]"
   ↓
6. Send to LLM
   └→ System prompt + context + user question
```

### Retrieval Configuration

**Vector Store Settings:**
```python
# backend/app/services/rag/vector_store.py
k = 3  # Top-K results
similarity_threshold = 0.7  # Minimum similarity score
```

**Optimization Parameters:**
- **Top-K:** 3 chunks (balance quality vs context window)
- **Chunk size:** ~500 tokens (enough context, fits in window)
- **Overlap:** 50 tokens (preserve continuity)

---

## KB Maintenance

### Adding New Documents

**1. Create markdown file:**
```bash
touch backend/data/kb/kb-new-feature.md
```

**2. Write content:**
```markdown
# New Feature Guide

## Overview
Description of the new feature...

## Procedure
Step-by-step instructions...

## Troubleshooting
Common issues...
```

**3. Run ingestion:**
```bash
python -m app.scripts.ingest
```

**4. Verify:**
```bash
# Query database
SELECT COUNT(*) FROM documents WHERE doc_metadata->>'source' LIKE '%kb-new-feature%';
```

### Updating Existing Documents

**1. Edit markdown file:**
```bash
vim backend/data/kb/kb-password-reset.md
```

**2. Clear old chunks (optional):**
```sql
DELETE FROM documents WHERE doc_metadata->>'source' = 'kb-password-reset.md';
```

**3. Re-ingest:**
```bash
python -m app.scripts.ingest
```

### Deleting Documents

**1. Remove file:**
```bash
rm backend/data/kb/obsolete-doc.md
```

**2. Clear from database:**
```sql
DELETE FROM documents WHERE doc_metadata->>'source' = 'obsolete-doc.md';
```

**3. Rebuild index (if needed):**
```sql
REINDEX INDEX documents_embedding_idx;
```

---

## KB Quality Guidelines

### Document Writing Best Practices

**1. Clear Structure:**
- Use H1 for title
- Use H2 for sections
- Use H3 for subsections
- Use code blocks for commands

**2. Actionable Content:**
- Step-by-step procedures
- Specific commands/values
- Expected outcomes
- Error messages with solutions

**3. Cross-References:**
- Link related documents
- Use relative paths
- Maintain link validity

**4. Metadata-Rich:**
- Descriptive titles
- Clear categories
- Version information (if applicable)

### Example Quality Document

```markdown
# Docker Container Initialization Failure

## Symptoms
- Container exits immediately after start
- Error: "exec format error"
- Status: Exited (127)

## Root Cause
Architecture mismatch (ARM vs x86)

## Solution

### Step 1: Check Image Architecture
```bash
docker inspect <image> | grep Architecture
```

### Step 2: Build for Correct Platform
```bash
docker build --platform linux/amd64 -t myimage .
```

### Step 3: Verify Container Runs
```bash
docker run myimage
```

## Prevention
Always specify platform in Dockerfile:
```dockerfile
FROM --platform=linux/amd64 node:18
```

## Related Issues
- [Container Runtime Troubleshooting](06-container-runtime-troubleshooting.md)
- [VM Crash Recovery](kb-vm-crash-recovery.md)
```

---

## Search Optimization

### Embedding Quality

**Model:** text-embedding-3-small
- Dimensions: 1536
- Max tokens: 8191
- Cost: $0.02 / 1M tokens

**Why This Model:**
- Good quality/cost balance
- Fast inference
- Semantic understanding
- Multilingual support

### Chunking Strategy

**Current Approach:**
```python
def chunk_document(text, max_chunk_size=500, overlap=50):
    # Split on headings first (H2, H3)
    sections = split_by_headings(text)
    
    # Further split long sections
    chunks = []
    for section in sections:
        if len(section) > max_chunk_size:
            chunks.extend(split_by_sentence(section, max_chunk_size, overlap))
        else:
            chunks.append(section)
    
    return chunks
```

**Benefits:**
- Preserves semantic units (sections)
- Maintains context (overlap)
- Fits in LLM context window

### Index Performance

**Query Speed:**
- IVFFlat: ~10ms for 10K docs
- HNSW: ~5ms for 10K docs

**Accuracy (Recall@K):**
- IVFFlat (lists=100): ~95%
- HNSW: ~99%

**Trade-offs:**
- IVFFlat: Faster index build, slightly lower recall
- HNSW: Slower build, better recall

---

## Monitoring KB Health

### KB Statistics Query

```sql
-- Total documents
SELECT COUNT(*) as total_chunks FROM documents;

-- Documents by source
SELECT doc_metadata->>'source' as source, COUNT(*) as chunks
FROM documents
GROUP BY source
ORDER BY chunks DESC;

-- Average chunk size
SELECT AVG(LENGTH(text)) as avg_chunk_length FROM documents;

-- Embedding dimension check
SELECT vector_dims(embedding) FROM documents LIMIT 1;
```

### KB Coverage Analysis

```python
# Check which categories are covered
categories = {}
for doc in documents:
    category = doc.metadata.get('category', 'uncategorized')
    categories[category] = categories.get(category, 0) + 1

print("KB Coverage:")
for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count} chunks")
```

---

## Troubleshooting

### Common Issues

**1. Ingestion Fails - OpenAI Error**
```bash
# Solution: Check API key
echo $OPENAI_API_KEY
# Set if missing
export OPENAI_API_KEY="sk-..."
```

**2. No Embeddings Generated**
```bash
# Solution: Check database connection
psql $DATABASE_URL_OVERRIDE -c "SELECT COUNT(*) FROM documents;"
```

**3. Poor Search Results**
```sql
-- Solution: Rebuild vector index
DROP INDEX documents_embedding_idx;
CREATE INDEX documents_embedding_idx 
ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**4. Slow Queries**
```sql
-- Solution: Analyze and vacuum
ANALYZE documents;
VACUUM FULL documents;
```

---

## Future Enhancements

### Planned Improvements

**1. Metadata Enrichment:**
- Document version tracking
- Last updated timestamps
- Author information
- Confidence scores

**2. Advanced Chunking:**
- Semantic chunking (not just paragraph-based)
- Dynamic chunk sizing
- Contextual overlap

**3. Multi-Modal KB:**
- Support for images (screenshots)
- Code snippet extraction
- Video transcripts

**4. Knowledge Graph:**
- Build relationship graph between docs
- Improved cross-referencing
- Concept clustering

---

## Summary

**KB Architecture:**
- ✅ 34 synthetic documents
- ✅ Markdown format
- ✅ PostgreSQL + pgvector storage
- ✅ OpenAI embeddings (1536-dim)
- ✅ Cosine similarity search
- ✅ Automated ingestion script

**Key Features:**
- Deterministic retrieval
- Source attribution
- Fast similarity search (10-20ms)
- Easy maintenance (add/edit/delete)

**This KB structure enables accurate, grounded AI responses!** ✅
